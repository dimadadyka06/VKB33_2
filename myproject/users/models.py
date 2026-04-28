import logging
import os

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


def validate_image_extension(value):
    """Проверяем, что загружаемый файл является изображением по расширению."""
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Файл «{value.name}» не является изображением. '
            f'Разрешённые форматы: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}.'
        )


class User(AbstractUser):
    bio = models.TextField(blank=True, verbose_name='О себе')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватарка',
        validators=[validate_image_extension],
    )
    friends = models.ManyToManyField(
        'self', blank=True, symmetrical=False,
        related_name='friend_of', verbose_name='Друзья',
    )
    friend_requests = models.ManyToManyField(
        'self', blank=True, symmetrical=False,
        related_name='incoming_requests', verbose_name='Заявки в друзья',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_friend(self, user):
        return self.friends.filter(pk=user.pk).exists()

    def has_sent_request(self, user):
        return self.friend_requests.filter(pk=user.pk).exists()
