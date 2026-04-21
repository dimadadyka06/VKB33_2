"""
conftest.py — общие фикстуры.
Файл должен лежать рядом с manage.py и pytest.ini
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import pytest
from django.test import Client
from users.models import User


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='StrongPass123!',
    )


@pytest.fixture
def user2(db):
    return User.objects.create_user(
        username='testuser2',
        email='testuser2@example.com',
        password='StrongPass123!',
    )


@pytest.fixture
def user3(db):
    return User.objects.create_user(
        username='testuser3',
        email='testuser3@example.com',
        password='StrongPass123!',
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123!',
    )


@pytest.fixture
def auth_client(client, user):
    client.login(username='testuser', password='StrongPass123!')
    return client


@pytest.fixture
def auth_client2(user2):
    c = Client()
    c.login(username='testuser2', password='StrongPass123!')
    return c


@pytest.fixture
def friends_pair(db, user, user2):
    user.friends.add(user2)
    user2.friends.add(user)
    return user, user2
