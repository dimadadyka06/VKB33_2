import logging
import os

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileEditForm, RegisterForm
from .models import User

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


# ──────────────────────────────────────────────
# Auth views
# ──────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(
                'New user registered successfully: username=%s email=%s',
                user.username, user.email,
            )
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    logger.warning(
                        'Registration validation error: field=%s error=%s '
                        'data_username=%s',
                        field, error,
                        form.data.get('username', '—'),
                    )
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def home(request):
    return render(request, 'home.html')


# ──────────────────────────────────────────────
# User list / profile
# ──────────────────────────────────────────────

@login_required
def user_list(request):
    """Список всех пользователей (только для авторизованных)."""
    all_users = User.objects.exclude(pk=request.user.pk)
    my_friends = set(request.user.friends.values_list('pk', flat=True))
    sent_requests = set(request.user.friend_requests.values_list('pk', flat=True))

    users = []
    for u in all_users:
        users.append({
            'user': u,
            'is_friend': u.pk in my_friends,
            'has_sent': u.pk in sent_requests,
        })

    return render(request, 'users/user_list.html', {'users': users})


@login_required
def profile(request, username):
    """Страница профиля."""
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    is_friend = request.user.is_friend(profile_user)
    has_sent = request.user.has_sent_request(profile_user)

    if not is_owner and not is_friend:
        return render(request, 'users/profile_private.html', {
            'profile_user': profile_user,
            'has_sent': has_sent,
        })

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'has_sent': has_sent,
    })


@login_required
def profile_edit(request):
    """Редактирование своего профиля (включая аватар)."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            try:
                form.save()
                logger.info('User %s updated their profile', request.user.username)
                messages.success(request, 'Профиль обновлён!')
                return redirect('profile', username=request.user.username)
            except Exception:
                logger.error(
                    'Unexpected error while saving profile for user %s',
                    request.user.username,
                    exc_info=True,
                )
                messages.error(request, 'Произошла ошибка при сохранении профиля.')
        else:
            # Логируем ошибки валидации, в том числе ошибки загрузки аватара
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'avatar':
                        avatar_file = request.FILES.get('avatar')
                        logger.error(
                            'Non-image file upload attempt by user %s: '
                            'filename=%s error=%s',
                            request.user.username,
                            avatar_file.name if avatar_file else '—',
                            error,
                            exc_info=True,
                        )
                    else:
                        logger.warning(
                            'Profile edit validation error for user %s: '
                            'field=%s error=%s',
                            request.user.username, field, error,
                        )
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})

# Friend management

@login_required
def send_friend_request(request, username):
    """Отправить заявку в друзья."""
    to_user = get_object_or_404(User, username=username)
    if to_user != request.user and not request.user.is_friend(to_user):
        request.user.friend_requests.add(to_user)
        logger.info(
            'Friend request sent: from=%s to=%s',
            request.user.username, to_user.username,
        )
        messages.success(request, f'Заявка отправлена пользователю {to_user.username}!')
    else:
        logger.warning(
            'Friend request skipped: from=%s to=%s (already friends or self)',
            request.user.username, to_user.username,
        )
    return redirect('profile', username=to_user.username)


@login_required
def accept_friend_request(request, username):
    """Принять заявку в друзья."""
    from_user = get_object_or_404(User, username=username)
    if from_user.has_sent_request(request.user):
        request.user.friends.add(from_user)
        from_user.friends.add(request.user)
        from_user.friend_requests.remove(request.user)
        logger.info(
            'Friend request accepted: user=%s accepted request from=%s',
            request.user.username, from_user.username,
        )
        messages.success(request, f'{from_user.username} теперь ваш друг!')
    else:
        logger.warning(
            'Accept friend request failed (no pending request): '
            'user=%s from=%s',
            request.user.username, from_user.username,
        )
    return redirect('profile', username=request.user.username)


@login_required
def remove_friend(request, username):
    """Удалить из друзей."""
    friend = get_object_or_404(User, username=username)
    if request.user.is_friend(friend):
        request.user.friends.remove(friend)
        friend.friends.remove(request.user)
        logger.info(
            'Friendship removed: user=%s removed friend=%s',
            request.user.username, friend.username,
        )
        messages.success(request, f'{friend.username} удалён из друзей.')
    else:
        logger.warning(
            'Remove friend failed (not friends): user=%s target=%s',
            request.user.username, friend.username,
        )
    return redirect('profile', username=request.user.username)


@login_required
def incoming_requests(request):
    """Входящие заявки в друзья."""
    requesters = User.objects.filter(friend_requests=request.user)
    return render(request, 'users/incoming_requests.html', {'requesters': requesters})
