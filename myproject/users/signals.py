"""
Сигналы для логирования событий аутентификации.
"""
import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    logger.info(
        'User logged in successfully: username=%s ip=%s',
        user.username,
        request.META.get('REMOTE_ADDR', 'unknown'),
    )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    logger.warning(
        'Failed login attempt: username=%s ip=%s',
        credentials.get('username', '—'),
        request.META.get('REMOTE_ADDR', 'unknown'),
    )
