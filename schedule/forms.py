import re
from datetime import date
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import Teacher, Course, Student


# ─────────────────────────────────────────────
#  КАСТОМНЫЕ ВАЛИДАТОРЫ  (не менее трёх)
# ─────────────────────────────────────────────

def validate_phone_format(value):
    """Валидатор 1: телефон должен начинаться с +7 и содержать 11 цифр."""
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    if not re.fullmatch(r'\+7\d{10}', cleaned):
        raise ValidationError(
            'Введите телефон в формате +7XXXXXXXXXX (11 цифр после +7).'
        )


def validate_no_digits_in_name(value):
    """Валидатор 2: имя/фамилия не должны содержать цифры."""
    if any(ch.isdigit() for ch in value):
        raise ValidationError('Имя не должно содержать цифры.')


def validate_not_future_start(value):
    """Валидатор 3: дата начала курса не должна быть раньше сегодня."""
    if value < date.today():
        raise ValidationError(
            'Дата начала курса не может быть в прошлом.'
        )


def validate_positive_price(value):
    """Валидатор 4: цена не может быть отрицательной."""
    if value < Decimal('0'):
        raise ValidationError('Цена не может быть отрицательной.')


def validate_experience_not_too_high(value):
    """Валидатор 5: опыт работы — разумное число (не более 70 лет)."""
    if value > 70:
        raise ValidationError('Укажите реальное число лет опыта (не более 70).')



#  ФОРМА ПРЕПОДАВАТЕЛЯ  (ModelForm)


class TeacherForm(forms.ModelForm):
    """ModelForm для создания и редактирования преподавателя."""

    # Переопределяем поля, чтобы навесить кастомные валидаторы
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        validators=[validate_no_digits_in_name],
        widget=forms.TextInput(attrs={'placeholder': 'Например: Иван'}),
    )
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        validators=[validate_no_digits_in_name],
        widget=forms.TextInput(attrs={'placeholder': 'Например: Иванов'}),
    )
    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        validators=[validate_phone_format],
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 000-00-00'}),
        help_text='Номер телефона в формате +7XXXXXXXXXX.',
    )
    experience_years = forms.IntegerField(
        label='Лет опыта',
        min_value=0,
        initial=0,
        validators=[validate_experience_not_too_high],
        help_text='Полное количество лет педагогического опыта.',
    )

    class Meta:
        model = Teacher
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'specialization', 'experience_years',
            'degree', 'hourly_rate', 'is_active', 'website',
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'example@university.ru'}),
            'specialization': forms.TextInput(attrs={'placeholder': 'Например: Математический анализ'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://'}),
            'hourly_rate': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
        }
        help_texts = {
            'email': 'Укажите рабочий email — он должен быть уникальным.',
            'hourly_rate': 'Почасовая ставка в рублях (0 — волонтёр).',
            'website': 'Необязательно. Личный сайт или портфолио.',
        }

    # ── clean_ методы (не менее трёх)

    def clean_email(self):
        """clean_ 1: email должен быть в домене .ru или .com."""
        email = self.cleaned_data.get('email', '')
        domain = email.split('@')[-1].lower() if '@' in email else ''
        if not (domain.endswith('.ru') or domain.endswith('.com')):
            raise ValidationError(
                'Допустимы только адреса в доменах .ru или .com.'
            )
        qs = Teacher.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Преподаватель с таким email уже существует.')
        return email

    def clean_first_name(self):
        """clean_ 2: приводим имя к формату «Первая буква заглавная»."""
        value = self.cleaned_data.get('first_name', '')
        return value.strip().capitalize()

    def clean_last_name(self):
        """clean_ 3: то же для фамилии."""
        value = self.cleaned_data.get('last_name', '')
        return value.strip().capitalize()

    def clean_hourly_rate(self):
        """clean_ 4: ставка не выше 100 000 руб/час."""
        rate = self.cleaned_data.get('hourly_rate')
        if rate is not None and rate > Decimal('100000'):
            raise ValidationError('Ставка не может превышать 100 000 руб/час.')
        return rate

    # ── clean() для формы (1 из 2)

    def clean(self):
        """
        cross-field: степень кандидата/доктора наук требует >= 5 лет опыта.
        """
        cleaned = super().clean()
        degree = cleaned.get('degree')
        experience = cleaned.get('experience_years')

        if degree in ('phd', 'doctor') and experience is not None and experience < 5:
            raise ValidationError(
                'Преподаватель со степенью кандидата/доктора наук '
                'должен иметь не менее 5 лет опыта.'
            )
        return cleaned


#  ФОРМА КУРСА  (ModelForm)


class CourseForm(forms.ModelForm):
    """ModelForm для создания и редактирования курса."""

    price = forms.DecimalField(
        max_digits=10, decimal_places=2,
        label='Цена (₽)',
        validators=[validate_positive_price],
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        help_text='Укажите 0 для бесплатных курсов.',
    )

    start_date = forms.DateField(
        label='Дата начала',
        validators=[validate_not_future_start],
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'teacher', 'level',
            'duration_weeks', 'price', 'start_date', 'end_date',
            'max_students', 'language', 'is_published', 'rating',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Основы Python'}),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Опишите чему научит этот курс...'
            }),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }
        help_texts = {
            'title': 'Введите понятное и краткое название курса.',
            'description': 'Подробно опишите программу и цели курса.',
            'teacher': 'Необязательно. Можно назначить позже.',
            'rating': 'Оценка от 0 до 10, кратная 0.5.',
        }

    # ── clean_ методы ───────────────────────────────────────────────────

    def clean_title(self):
        """clean_ 1: название курса не короче 5 символов."""
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 5:
            raise ValidationError(
                'Название курса должно содержать не менее 5 символов.'
            )
        return title

    def clean_duration_weeks(self):
        """clean_ 2: длительность от 1 до 104 недель."""
        weeks = self.cleaned_data.get('duration_weeks')
        if weeks is not None:
            if weeks < 1:
                raise ValidationError('Длительность должна быть не менее 1 недели.')
            if weeks > 104:
                raise ValidationError('Длительность не может превышать 104 недели (2 года).')
        return weeks

    def clean_max_students(self):
        """clean_ 3: максимум студентов от 1 до 500."""
        max_s = self.cleaned_data.get('max_students')
        if max_s is not None:
            if max_s < 1:
                raise ValidationError('Минимальное число студентов — 1.')
            if max_s > 500:
                raise ValidationError('Максимальное число студентов — 500.')
        return max_s

    def clean_rating(self):
        """clean_ 4: рейтинг кратен 0.5."""
        rating = self.cleaned_data.get('rating')
        if rating is not None:
            remainder = int(rating * 2) % 1
            if float(rating * 2) != int(rating * 2):
                raise ValidationError(
                    'Рейтинг должен быть кратен 0.5 (например: 7.0, 7.5, 8.0).'
                )
        return rating

    # ── clean() для формы (2 из 2) ───────────────────────────────────────

    def clean(self):
        """
        cross-field: дата окончания > дата начала,
        разница ≈ duration_weeks (±1 неделя).
        """
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        weeks = cleaned.get('duration_weeks')

        if start and end:
            if end <= start:
                raise ValidationError(
                    'Дата окончания должна быть позже даты начала.'
                )
            if weeks:
                delta_weeks = (end - start).days / 7
                if abs(delta_weeks - weeks) > 1:
                    raise ValidationError(
                        f'Разница между датами ({delta_weeks:.1f} нед.) '
                        f'не соответствует указанной длительности ({weeks} нед.). '
                        f'Допустимое расхождение — не более 1 недели.'
                    )
        return cleaned



#  ФОРМА СТУДЕНТА  (ModelForm)


class StudentForm(forms.ModelForm):
    """ModelForm для создания и редактирования студента."""

    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        validators=[validate_no_digits_in_name],
        widget=forms.TextInput(attrs={'placeholder': 'Имя'}),
    )
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        validators=[validate_no_digits_in_name],
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}),
    )

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'birth_date', 'status', 'city', 'gpa',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'email': forms.EmailInput(attrs={'placeholder': 'student@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 000-00-00'}),
            'city': forms.TextInput(attrs={'placeholder': 'Москва'}),
            'gpa': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '4.50'}),
        }
        help_texts = {
            'phone': 'Необязательно. Формат +7XXXXXXXXXX.',
            'birth_date': 'Необязательно.',
            'gpa': 'Средний балл от 0.00 до 5.00.',
        }

    # ── clean_ методы ───────────────────────────────────────────────────

    def clean_email(self):
        """clean_ 1: уникальность email студента."""
        email = self.cleaned_data.get('email', '')
        qs = Student.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Студент с таким email уже зарегистрирован.')
        return email

    def clean_birth_date(self):
        """clean_ 2: возраст от 14 до 100 лет."""
        bd = self.cleaned_data.get('birth_date')
        if bd:
            today = date.today()
            age = (today - bd).days // 365
            if age < 14:
                raise ValidationError('Студент должен быть не моложе 14 лет.')
            if age > 100:
                raise ValidationError('Проверьте дату рождения — возраст превышает 100 лет.')
        return bd

    def clean_phone(self):
        """clean_ 3: валидация телефона, если он введён."""
        phone = self.cleaned_data.get('phone', '')
        if phone:
            validate_phone_format(phone)
        return phone

    def clean_gpa(self):
        """clean_ 4: GPA от 0 до 5."""
        gpa = self.cleaned_data.get('gpa')
        if gpa is not None:
            if gpa < 0:
                raise ValidationError('GPA не может быть отрицательным.')
            if gpa > 5:
                raise ValidationError('GPA не может превышать 5.00.')
        return gpa

    # ── clean() — cross-field

    def clean(self):
        """
        cross-field: неактивный студент с GPA > 4.5 — вероятная ошибка данных.
        """
        cleaned = super().clean()
        status = cleaned.get('status')
        gpa = cleaned.get('gpa')

        if status == 'inactive' and gpa is not None and gpa > Decimal('4.5'):
            raise ValidationError(
                'Студент с высоким GPA (> 4.5) не может иметь статус «Неактивен». '
                'Проверьте введённые данные.'
            )
        return cleaned
