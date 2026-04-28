import logging
import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Номер телефона')

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'name'):
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                msg = (
                    f'Файл «{avatar.name}» не является изображением. '
                    f'Разрешённые форматы: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}.'
                )
                logger.warning(
                    'User attempted to upload non-image file: %s (ext=%s)',
                    avatar.name, ext,
                )
                raise ValidationError(msg)
        return avatar
