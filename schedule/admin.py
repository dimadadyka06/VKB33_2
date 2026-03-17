# schedule/admin.py

from django.contrib import admin
from django.db.models import Count
from .models import Teacher, TeacherInfo, Course, Student, Enrollment


class CourseCountFilter(admin.SimpleListFilter):
    """Фильтр для преподавателей по количеству курсов"""
    title = 'Количество курсов'
    parameter_name = 'course_count'

    def lookups(self, request, model_admin):
        return (
            ('0', '0 курсов'),
            ('1', '1 курс'),
            ('2', '2 и более'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(c=Count('courses'))
        if self.value() == '0':
            return queryset.filter(c=0)
        if self.value() == '1':
            return queryset.filter(c=1)
        if self.value() == '2':
            return queryset.filter(c__gte=2)
        return queryset


class TeacherProfileFilter(admin.SimpleListFilter):
    """Фильтр для преподавателей по наличию профиля"""
    title = 'Наличие профиля'
    parameter_name = 'has_profile'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С профилем'),
            ('no', 'Без профиля'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(info__isnull=False)
        if self.value() == 'no':
            return queryset.filter(info__isnull=True)
        return queryset


class StudentCourseFilter(admin.SimpleListFilter):
    """Фильтр для студентов по наличию курсов"""
    title = 'Наличие курсов'
    parameter_name = 'has_courses'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'С курсами'),
            ('no', 'Без курсов'),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(c=Count('enrollments'))
        if self.value() == 'yes':
            return queryset.filter(c__gt=0)
        if self.value() == 'no':
            return queryset.filter(c=0)
        return queryset



class TeacherInfoInline(admin.StackedInline):
    """Inline для отображения доп. информации о преподавателе"""
    model = TeacherInfo
    can_delete = False
    verbose_name = "Дополнительная информация"
    verbose_name_plural = "Дополнительная информация"
    fields = ['bio', 'education']


class EnrollmentInline(admin.TabularInline):
    """Inline для отображения записей на курсы"""
    model = Enrollment
    extra = 0
    verbose_name = "Запись на курс"
    verbose_name_plural = "Записи на курс"
    fields = ['course', 'status', 'enrollment_date']
    readonly_fields = ['enrollment_date']
    autocomplete_fields = ['course']


class CourseInline(admin.TabularInline):
    """Inline для отображения курсов преподавателя"""
    model = Course
    extra = 0
    verbose_name = "Курс"
    verbose_name_plural = "Курсы преподавателя"
    fields = ['title', 'level', 'price', 'start_date']
    readonly_fields = ['title', 'level', 'price', 'start_date']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False



@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Админка для преподавателей"""
    list_display = ['last_name', 'first_name', 'email', 'specialization', 'experience_years', 'course_count',
                    'has_profile']
    list_filter = [CourseCountFilter, TeacherProfileFilter, 'specialization']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']
    inlines = [TeacherInfoInline, CourseInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Профессиональная информация', {
            'fields': ('specialization', 'experience_years')
        }),
    )

    def get_queryset(self, request):
        """Оптимизация запросов и добавление аннотаций"""
        return super().get_queryset(request).annotate(
            course_count_annotated=Count('courses', distinct=True)
        ).select_related('info')

    def course_count(self, obj):
        """Количество курсов у преподавателя"""
        return getattr(obj, 'course_count_annotated', obj.courses.count())

    course_count.short_description = 'Курсов'
    course_count.admin_order_field = 'course_count_annotated'

    def has_profile(self, obj):
        """Проверка наличия профиля"""
        return hasattr(obj, 'info')

    has_profile.short_description = 'Профиль'
    has_profile.boolean = True


@admin.register(TeacherInfo)
class TeacherInfoAdmin(admin.ModelAdmin):
    """Админка для дополнительной информации преподавателей"""
    list_display = ['teacher', 'education']
    list_select_related = ['teacher']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'education']

    fieldsets = (
        ('Преподаватель', {
            'fields': ('teacher',)
        }),
        ('Информация', {
            'fields': ('bio', 'education')
        }),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админка для курсов"""
    list_display = ['title', 'teacher', 'level', 'price', 'start_date', 'student_count']
    list_filter = ['level', 'teacher', 'start_date']
    search_fields = ['title', 'description', 'teacher__first_name', 'teacher__last_name']
    ordering = ['-start_date']
    inlines = [EnrollmentInline]
    autocomplete_fields = ['teacher']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'teacher')
        }),
        ('Детали курса', {
            'fields': ('level', 'duration_weeks', 'price')
        }),
        ('Даты', {
            'fields': ('start_date', 'end_date')
        }),
        ('Ограничения', {
            'fields': ('max_students',)
        }),
    )

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).annotate(
            student_count_annotated=Count('enrollments', distinct=True)
        ).select_related('teacher')

    def student_count(self, obj):
        """Количество студентов на курсе"""
        return getattr(obj, 'student_count_annotated', obj.enrollments.count())

    student_count.short_description = 'Студентов'
    student_count.admin_order_field = 'student_count_annotated'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Админка для студентов"""
    list_display = ['last_name', 'first_name', 'email', 'status', 'enrolled_date', 'course_count']
    list_filter = [StudentCourseFilter, 'status', 'enrolled_date']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']
    inlines = [EnrollmentInline]

    fieldsets = (
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date')
        }),
        ('Статус', {
            'fields': ('status', 'enrolled_date')
        }),
    )

    readonly_fields = ['enrolled_date']

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).annotate(
            course_count_annotated=Count('enrollments', distinct=True)
        )

    def course_count(self, obj):
        """Количество курсов у студента"""
        return getattr(obj, 'course_count_annotated', obj.enrollments.count())

    course_count.short_description = 'Курсов'
    course_count.admin_order_field = 'course_count_annotated'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Админка для записей на курсы"""
    list_display = ['student', 'course', 'status', 'enrollment_date']
    list_filter = ['status', 'enrollment_date']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    ordering = ['-enrollment_date']
    autocomplete_fields = ['student', 'course']

    fieldsets = (
        (None, {
            'fields': ('student', 'course', 'status')
        }),
        ('Детали', {
            'fields': ('enrollment_date',)
        }),
    )

    readonly_fields = ['enrollment_date']



admin.site.site_header = "Система управления курсами"
admin.site.site_title = "Каталог курсов"
admin.site.index_title = "Панель администратора"