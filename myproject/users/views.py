from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileEditForm
from .models import User


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # автологин после регистрации
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def home(request):
    return render(request, 'home.html')


@login_required
def user_list(request):
    """Список всех пользователей (только для авторизованных)"""
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
    """Страница профиля"""
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    is_friend = request.user.is_friend(profile_user)
    has_sent = request.user.has_sent_request(profile_user)



    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'has_sent': has_sent,
    })


@login_required
def profile_edit(request):
    """Редактирование своего профиля"""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def send_friend_request(request, username):
    """Отправить заявку в друзья"""
    to_user = get_object_or_404(User, username=username)
    if to_user != request.user and not request.user.is_friend(to_user):
        request.user.friend_requests.add(to_user)
        messages.success(request, f'Заявка отправлена пользователю {to_user.username}!')
    return redirect('user_list')


@login_required
def accept_friend_request(request, username):
    """Принять заявку в друзья"""
    from_user = get_object_or_404(User, username=username)
    # from_user отправил заявку — значит у from_user в friend_requests есть request.user
    if from_user.has_sent_request(request.user):
        request.user.friends.add(from_user)
        from_user.friends.add(request.user)
        from_user.friend_requests.remove(request.user)
        messages.success(request, f'{from_user.username} теперь ваш друг!')
    return redirect('profile', username=request.user.username)


@login_required
def remove_friend(request, username):
    """Удалить из друзей"""
    friend = get_object_or_404(User, username=username)
    request.user.friends.remove(friend)
    friend.friends.remove(request.user)
    messages.success(request, f'{friend.username} удалён из друзей.')
    return redirect('profile', username=request.user.username)


@login_required
def incoming_requests(request):
    """Входящие заявки в друзья"""
    # Люди, которые отправили заявку текущему пользователю
    requesters = User.objects.filter(friend_requests=request.user)
    return render(request, 'users/incoming_requests.html', {'requesters': requesters})
