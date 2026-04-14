from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(blank=True, verbose_name='О себе')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    friends = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='friend_of', verbose_name='Друзья')
    friend_requests = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='incoming_requests', verbose_name='Заявки в друзья')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_friend(self, user):
        return self.friends.filter(pk=user.pk).exists()

    def has_sent_request(self, user):
        return self.friend_requests.filter(pk=user.pk).exists()
