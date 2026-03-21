from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Модель Teacher (Преподаватель)
class Teacher(models.Model):
    DEGREE_CHOICES = [
        ('none', 'Без степени'),
        ('bachelor', 'Бакалавр'),
        ('master', 'Магистр'),
        ('phd', 'Кандидат наук'),
        ('doctor', 'Доктор наук'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    specialization = models.CharField(max_length=200, blank=True, verbose_name="Специализация")
    experience_years = models.IntegerField(default=0, verbose_name="Лет опыта")
    # Новые поля
    degree = models.CharField(
        max_length=20, choices=DEGREE_CHOICES, default='none',
        verbose_name="Учёная степень"
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Ставка (руб/час)"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    website = models.URLField(blank=True, verbose_name="Сайт/Портфолио")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"


# Модель TeacherInfo (Доп. информация о преподавателе)  1 К 1
class TeacherInfo(models.Model):
    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,#При удалении преподавателя автоматически удаляется его профиль
        related_name='info',
        verbose_name="Преподаватель"
    )
    bio = models.TextField(max_length=1000, blank=True, verbose_name="Биография")
    education = models.CharField(max_length=300, blank=True, verbose_name="Образование")

    def __str__(self):
        return f"Информация: {self.teacher}"

    class Meta:
        verbose_name = "Доп. информация"
        verbose_name_plural = "Доп. информация"


# Модель Course (Курс)
class Course(models.Model):   # 1 К N
    LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание")

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name="Преподаватель"
    )

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', verbose_name="Уровень")
    duration_weeks = models.IntegerField(default=4, verbose_name="Длительность (недель)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    max_students = models.IntegerField(default=10, verbose_name="Макс. студентов")
    # Новые поля
    language = models.CharField(
        max_length=50, default='Русский',
        verbose_name="Язык обучения"
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="Рейтинг (0–10)"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


# Модель Student (Студент)
class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    enrolled_date = models.DateField(auto_now_add=True, verbose_name="Дата регистрации")
    # Новые поля
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    gpa = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Средний балл (GPA, 0–5)"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"


# Модель Enrollment (Запись на курс)
class Enrollment(models.Model):   # N к N
    STATUS_CHOICES = [
        ('enrolled', 'Записан'),
        ('completed', 'Завершен'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Курс")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled', verbose_name="Статус")

    class Meta:
        unique_together = ['student', 'course']  # Студент не может записаться на один курс дважды
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курс"

    def __str__(self):
        return f"{self.student} - {self.course}"