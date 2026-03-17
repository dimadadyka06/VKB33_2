from django import forms


class TeacherForm(forms.Form):

    first_name = forms.CharField(
        label='Имя',
        max_length=100,
        help_text='Введите имя преподавателя (не более 100 символов)',
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: Иван',
        })
    )

    last_name = forms.CharField(
        label='Фамилия',
        max_length=100,
        help_text='Введите фамилию преподавателя',
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: Иванов',
        })
    )

    email = forms.EmailField(
        label='Email',
        help_text='Укажите рабочий email — он должен быть уникальным',
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@university.ru',
        })
    )

    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        help_text='Номер телефона в формате +7XXXXXXXXXX',
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (999) 000-00-00',
        })
    )

    specialization = forms.CharField(
        label='Специализация',
        max_length=200,
        required=False,           # Необязательное поле
        help_text='Необязательно. Область знаний или специализация преподавателя',
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: Математический анализ',
        })
    )

    experience_years = forms.IntegerField(
        label='Лет опыта',
        min_value=0,
        initial=0,
        help_text='Укажите полное количество лет педагогического опыта',
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
        })
    )
