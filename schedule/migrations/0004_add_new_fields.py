from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_alter_course_options_alter_enrollment_options_and_more'),
    ]

    operations = [
        # ── Teacher: новые поля ──────────────────────────────────────────
        migrations.AddField(
            model_name='teacher',
            name='degree',
            field=models.CharField(
                choices=[
                    ('none', 'Без степени'),
                    ('bachelor', 'Бакалавр'),
                    ('master', 'Магистр'),
                    ('phd', 'Кандидат наук'),
                    ('doctor', 'Доктор наук'),
                ],
                default='none',
                max_length=20,
                verbose_name='Учёная степень',
            ),
        ),
        migrations.AddField(
            model_name='teacher',
            name='hourly_rate',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=8,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name='Ставка (руб/час)',
            ),
        ),
        migrations.AddField(
            model_name='teacher',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='website',
            field=models.URLField(blank=True, verbose_name='Сайт/Портфолио'),
        ),

        # ── Course: новые поля ───────────────────────────────────────────
        migrations.AddField(
            model_name='course',
            name='language',
            field=models.CharField(
                default='Русский',
                max_length=50,
                verbose_name='Язык обучения',
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name='Опубликован'),
        ),
        migrations.AddField(
            model_name='course',
            name='rating',
            field=models.DecimalField(
                decimal_places=1,
                default=0,
                max_digits=3,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(10),
                ],
                verbose_name='Рейтинг (0–10)',
            ),
        ),

        # ── Student: новые поля ──────────────────────────────────────────
        migrations.AddField(
            model_name='student',
            name='city',
            field=models.CharField(blank=True, max_length=100, verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='student',
            name='gpa',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=4,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(5),
                ],
                verbose_name='Средний балл (GPA, 0–5)',
            ),
        ),
    ]
