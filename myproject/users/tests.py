"""
tests.py — Лабораторная работа 6: Тестирование Django-проекта.

Покрытие:
  - Регистрация пользователей
  - Вход / выход
  - Проверка доступа (авторизация — login_required)
  - Проверка permissions (кто может видеть профиль)
  - Проверка редиректов (assertRedirects)
  - Использование фикстур (conftest.py)
  - Параметризация тестов
  - Тестирование ошибок (невалидные данные, 404 и т.д.)
"""

import pytest
from django.urls import reverse
from users.models import User



# 1. Тесты регистрации


@pytest.mark.django_db
class TestRegistration:
    """Тесты представления register (POST /register/)."""

    def test_register_page_get(self, client):
        """GET /register/ возвращает 200 и форму регистрации."""
        url = reverse('register')
        response = client.get(url)
        assert response.status_code == 200
        assert 'form' in response.context

    def test_register_success(self, client):
        """Успешная регистрация создаёт пользователя и редиректит на home."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '+79001234567',
            'password1': 'UniquePass999!',
            'password2': 'UniquePass999!',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(username='newuser').exists()

    def test_register_redirect_to_home(self, client):
        """После успешной регистрации происходит редирект на '/' (home)."""
        url = reverse('register')
        data = {
            'username': 'redirectuser',
            'email': 'redir@example.com',
            'password1': 'UniquePass999!',
            'password2': 'UniquePass999!',
        }
        response = client.post(url, data)
        assert response['Location'] == reverse('home')

    def test_register_auto_login(self, client):
        """После регистрации пользователь автоматически входит в систему."""
        url = reverse('register')
        data = {
            'username': 'autologinuser',
            'email': 'auto@example.com',
            'password1': 'UniquePass999!',
            'password2': 'UniquePass999!',
        }
        client.post(url, data)
        response = client.get(reverse('user_list'))
        assert response.status_code == 200

    @pytest.mark.parametrize('data,expected_error_field', [
        (
            {
                'username': '',
                'email': 'x@example.com',
                'password1': 'UniquePass999!',
                'password2': 'UniquePass999!',
            },
            'username',
        ),
        (
            {
                'username': 'someuser',
                'email': 'not-an-email',
                'password1': 'UniquePass999!',
                'password2': 'UniquePass999!',
            },
            'email',
        ),
        (
            {
                'username': 'someuser2',
                'email': 'some@example.com',
                'password1': 'UniquePass999!',
                'password2': 'DifferentPass!',
            },
            'password2',
        ),
        (
            {
                'username': 'someuser3',
                'email': 'some3@example.com',
                'password1': '123',
                'password2': '123',
            },
            'password2',
        ),
    ])
    def test_register_invalid_data(self, client, data, expected_error_field):
        """Невалидные данные: форма возвращает 200 с ошибками."""
        url = reverse('register')
        response = client.post(url, data)
        assert response.status_code == 200
        form = response.context['form']
        assert not form.is_valid()
        assert expected_error_field in form.errors

    def test_register_duplicate_username(self, client, user):
        """Нельзя зарегистрироваться с уже существующим username."""
        url = reverse('register')
        data = {
            'username': user.username,
            'email': 'unique@example.com',
            'password1': 'UniquePass999!',
            'password2': 'UniquePass999!',
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert 'username' in response.context['form'].errors

    def test_register_duplicate_email(self, client, user):
        """Нельзя зарегистрироваться с уже существующим email."""
        url = reverse('register')
        data = {
            'username': 'brandnewuser',
            'email': user.email,
            'password1': 'UniquePass999!',
            'password2': 'UniquePass999!',
        }
        response = client.post(url, data)
        assert response.status_code == 200
        assert 'email' in response.context['form'].errors


# ===========================================================================
# 2. Тесты входа / выхода
# ===========================================================================

@pytest.mark.django_db
class TestLoginLogout:
    """Тесты входа и выхода через django.contrib.auth.urls."""

    def test_login_page_get(self, client):
        """GET /auth/login/ возвращает 200."""
        url = reverse('login')
        response = client.get(url)
        assert response.status_code == 200

    def test_login_success(self, client, user):
        """Успешный вход редиректит на LOGIN_REDIRECT_URL (/)."""
        url = reverse('login')
        response = client.post(url, {
            'username': user.username,
            'password': 'StrongPass123!',
        })
        assert response.status_code == 302
        assert response['Location'] == '/'

    def test_login_redirect(self, client, user):
        """assertRedirects: после логина перенаправляет на '/'."""
        url = reverse('login')
        response = client.post(url, {
            'username': user.username,
            'password': 'StrongPass123!',
        }, follow=True)
        assert response.redirect_chain[-1][0] == '/'

    @pytest.mark.parametrize('username,password', [
        ('testuser', 'wrongpassword'),
        ('nonexistent', 'StrongPass123!'),
        ('', ''),
        ('testuser', ''),
    ])
    def test_login_invalid_credentials(self, client, user, username, password):
        """Неверные учётные данные: возвращается 200 (не редирект)."""
        url = reverse('login')
        response = client.post(url, {
            'username': username,
            'password': password,
        })
        assert response.status_code == 200

    def test_logout_success(self, auth_client):
        """POST /auth/logout/ — редирект после выхода."""
        url = reverse('logout')
        response = auth_client.post(url)
        assert response.status_code == 302

    def test_logout_redirect(self, auth_client):
        """assertRedirects: после логаута перенаправляет на '/'."""
        url = reverse('logout')
        response = auth_client.post(url, follow=True)
        assert response.redirect_chain[-1][0] == '/'

    def test_logout_clears_session(self, auth_client):
        """После выхода /users/ для анонима → редирект на login."""
        auth_client.post(reverse('logout'))
        response = auth_client.get(reverse('user_list'))
        assert response.status_code == 302
        assert '/auth/login/' in response['Location']



# 3. Тесты авторизации (login_required)


@pytest.mark.django_db
class TestLoginRequired:
    """Проверяем, что защищённые страницы недоступны анонимам."""

    @pytest.mark.parametrize('url_name,kwargs', [
        ('user_list', {}),
        ('profile', {'username': 'testuser'}),
        ('profile_edit', {}),
        ('send_friend_request', {'username': 'testuser'}),
        ('accept_friend_request', {'username': 'testuser'}),
        ('remove_friend', {'username': 'testuser'}),
        ('incoming_requests', {}),
    ])
    def test_anonymous_redirected_to_login(self, client, user, url_name, kwargs):
        """Аноним → редирект на /auth/login/?next=..."""
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == 302
        assert '/auth/login/' in response['Location']

    @pytest.mark.parametrize('url_name,kwargs', [
        ('user_list', {}),
        ('profile_edit', {}),
        ('incoming_requests', {}),
    ])
    def test_authenticated_user_can_access(self, auth_client, url_name, kwargs):
        """Авторизованный пользователь получает доступ."""
        url = reverse(url_name, kwargs=kwargs)
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_anonymous_profile_redirect_contains_next(self, client, user):
        """При редиректе анонима в query-параметре next — исходный URL."""
        url = reverse('profile', kwargs={'username': user.username})
        response = client.get(url)
        assert response.status_code == 302
        location = response['Location']
        assert 'next=' in location
        assert user.username in location



# 4. Тесты permissions


@pytest.mark.django_db
class TestProfilePermissions:
    """Кто и что видит на странице профиля."""

    def test_owner_sees_own_profile(self, auth_client, user):
        """Владелец видит свой полный профиль."""
        url = reverse('profile', kwargs={'username': user.username})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.templates[0].name == 'users/profile.html'

    def test_non_friend_sees_private_profile(self, auth_client, user2):
        """Не-друг видит заглушку profile_private.html."""
        url = reverse('profile', kwargs={'username': user2.username})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.templates[0].name == 'users/profile_private.html'

    def test_friend_sees_full_profile(self, auth_client, user, user2):
        """Друг видит полный профиль."""
        user.friends.add(user2)
        user2.friends.add(user)
        url = reverse('profile', kwargs={'username': user2.username})
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.templates[0].name == 'users/profile.html'

    def test_profile_not_found_returns_404(self, auth_client):
        """Профиль несуществующего пользователя → 404."""
        url = reverse('profile', kwargs={'username': 'nobody_exists'})
        response = auth_client.get(url)
        assert response.status_code == 404

    def test_admin_user_list_accessible(self, client, admin_user):
        """Суперпользователь имеет доступ к /users/."""
        client.login(username='admin', password='AdminPass123!')
        response = client.get(reverse('user_list'))
        assert response.status_code == 200

    def test_user_list_excludes_self(self, auth_client, user, user2, user3):
        """В списке пользователей нет самого себя."""
        response = auth_client.get(reverse('user_list'))
        assert response.status_code == 200
        displayed = [u['user'] for u in response.context['users']]
        assert user not in displayed
        assert user2 in displayed
        assert user3 in displayed



# 5. Тесты редиректов


@pytest.mark.django_db
class TestRedirects:
    """Проверка редиректов (assertRedirects-стиль через redirect_chain)."""

    def test_register_redirects_to_home(self, client):
        """Регистрация → home."""
        url = reverse('register')
        data = {
            'username': 'redircheck',
            'email': 'redircheck@example.com',
            'password1': 'UniquePass999!',
            'password2': 'UniquePass999!',
        }
        response = client.post(url, data, follow=True)
        assert response.redirect_chain[0][0] == reverse('home')
        assert response.redirect_chain[0][1] == 302

    def test_login_redirects_to_home(self, client, user):
        """Вход → '/'."""
        response = client.post(reverse('login'), {
            'username': user.username,
            'password': 'StrongPass123!',
        }, follow=True)
        assert response.redirect_chain[0][0] == '/'
        assert response.redirect_chain[0][1] == 302

    def test_logout_redirects_to_home(self, auth_client):
        """Выход → '/'."""
        response = auth_client.post(reverse('logout'), follow=True)
        assert response.redirect_chain[0][0] == '/'
        assert response.redirect_chain[0][1] == 302

    def test_profile_edit_redirects_to_profile(self, auth_client, user):
        """Сохранение профиля → редирект на страницу профиля."""
        url = reverse('profile_edit')
        data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': user.email,
            'phone': '+79001112233',
            'bio': 'Тестовая биография',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert response['Location'] == reverse('profile', kwargs={'username': user.username})

    def test_send_friend_request_redirects_to_profile(self, auth_client, user2):
        """Отправка заявки → профиль адресата."""
        url = reverse('send_friend_request', kwargs={'username': user2.username})
        response = auth_client.post(url)
        assert response.status_code == 302
        assert response['Location'] == reverse('profile', kwargs={'username': user2.username})

    def test_accept_friend_request_redirects_to_own_profile(self, auth_client, user, user2):
        """Принятие заявки → свой профиль."""
        user2.friend_requests.add(user)
        url = reverse('accept_friend_request', kwargs={'username': user2.username})
        response = auth_client.post(url)
        assert response.status_code == 302
        assert response['Location'] == reverse('profile', kwargs={'username': user.username})

    def test_remove_friend_redirects_to_own_profile(self, auth_client, user, user2):
        """Удаление друга → свой профиль."""
        user.friends.add(user2)
        user2.friends.add(user)
        url = reverse('remove_friend', kwargs={'username': user2.username})
        response = auth_client.post(url)
        assert response.status_code == 302
        assert response['Location'] == reverse('profile', kwargs={'username': user.username})

    def test_anonymous_send_request_redirects_to_login(self, client, user2):
        """Аноним пытается отправить заявку → логин."""
        url = reverse('send_friend_request', kwargs={'username': user2.username})
        response = client.post(url)
        assert response.status_code == 302
        assert '/auth/login/' in response['Location']



# 6. Тесты дружбы


@pytest.mark.django_db
class TestFriendship:
    """Отправка/принятие/удаление заявок и проверка дружбы."""

    def test_send_friend_request(self, auth_client, user, user2):
        """Отправка заявки: user2 появляется в friend_requests user'а."""
        url = reverse('send_friend_request', kwargs={'username': user2.username})
        auth_client.post(url)
        user.refresh_from_db()
        assert user.has_sent_request(user2)

    def test_cannot_send_request_to_self(self, auth_client, user):
        """Нельзя отправить заявку самому себе."""
        url = reverse('send_friend_request', kwargs={'username': user.username})
        auth_client.post(url)
        user.refresh_from_db()
        assert not user.has_sent_request(user)

    def test_accept_friend_request(self, auth_client, user, user2):
        """Принятие заявки: оба становятся друзьями."""
        user2.friend_requests.add(user)
        url = reverse('accept_friend_request', kwargs={'username': user2.username})
        auth_client.post(url)
        user.refresh_from_db()
        user2.refresh_from_db()
        assert user.is_friend(user2)
        assert user2.is_friend(user)

    def test_remove_friend(self, auth_client, user, user2):
        """Удаление из друзей: дружба разрывается с обеих сторон."""
        user.friends.add(user2)
        user2.friends.add(user)
        url = reverse('remove_friend', kwargs={'username': user2.username})
        auth_client.post(url)
        user.refresh_from_db()
        user2.refresh_from_db()
        assert not user.is_friend(user2)
        assert not user2.is_friend(user)

    def test_incoming_requests_page(self, auth_client, user, user2):
        """На странице входящих заявок отображается отправитель."""
        user2.friend_requests.add(user)
        response = auth_client.get(reverse('incoming_requests'))
        assert response.status_code == 200
        requesters = list(response.context['requesters'])
        assert user2 in requesters

    @pytest.mark.parametrize('sender_username', [
        'testuser2',
        'testuser3',
    ])
    def test_multiple_friend_requests(self, auth_client, user, user2, user3, sender_username):
        """Несколько пользователей могут отправить заявки одному."""
        sender = User.objects.get(username=sender_username)
        sender.friend_requests.add(user)
        response = auth_client.get(reverse('incoming_requests'))
        requesters = list(response.context['requesters'])
        assert sender in requesters



# 7. Тесты ошибок


@pytest.mark.django_db
class TestErrors:
    """404, невалидные данные, граничные случаи."""

    def test_profile_404_for_unknown_user(self, auth_client):
        """Профиль несуществующего пользователя → 404."""
        url = reverse('profile', kwargs={'username': 'ghost_user'})
        response = auth_client.get(url)
        assert response.status_code == 404

    def test_send_request_404_for_unknown_user(self, auth_client):
        """Заявка несуществующему → 404."""
        url = reverse('send_friend_request', kwargs={'username': 'ghost_user'})
        response = auth_client.post(url)
        assert response.status_code == 404

    def test_accept_request_404_for_unknown_user(self, auth_client):
        """Принятие заявки от несуществующего → 404."""
        url = reverse('accept_friend_request', kwargs={'username': 'ghost_user'})
        response = auth_client.post(url)
        assert response.status_code == 404

    def test_remove_friend_404_for_unknown_user(self, auth_client):
        """Удаление несуществующего → 404."""
        url = reverse('remove_friend', kwargs={'username': 'ghost_user'})
        response = auth_client.post(url)
        assert response.status_code == 404

    @pytest.mark.parametrize('bad_email', [
        '',
        'not-an-email',
        'missing@',
        '@nodomain',
    ])
    def test_profile_edit_invalid_email(self, auth_client, user, bad_email):
        """Невалидный email при редактировании профиля → ошибка формы."""
        url = reverse('profile_edit')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': bad_email,
            'phone': '',
            'bio': '',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200
        form = response.context['form']
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_register_missing_all_fields(self, client):
        """Пустая форма регистрации → ошибки обязательных полей."""
        url = reverse('register')
        response = client.post(url, {})
        assert response.status_code == 200
        form = response.context['form']
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'email' in form.errors
        assert 'password1' in form.errors

    def test_home_page_accessible_to_anonymous(self, client):
        """Главная страница доступна без авторизации."""
        response = client.get(reverse('home'))
        assert response.status_code == 200

    def test_nonexistent_url_returns_404(self, client):
        """Несуществующий URL → 404."""
        response = client.get('/this/url/does/not/exist/')
        assert response.status_code == 404
