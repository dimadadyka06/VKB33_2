from django.shortcuts import render, get_object_or_404, redirect
from .forms import TeacherForm
from django.db.models import Count
from django.http import HttpResponseNotFound
from .models import Teacher, TeacherInfo, Course, Student, Enrollment


# ГЛАВНАЯ

def index(request):
    """Главная страница приложения schedule"""
    teachers_count = Teacher.objects.count()
    courses_count = Course.objects.count()
    students_count = Student.objects.count()
    enrollments_count = Enrollment.objects.count()

    context = {
        'teachers_count': teachers_count,
        'courses_count': courses_count,
        'students_count': students_count,
        'enrollments_count': enrollments_count,
    }
    return render(request, 'schedule/index.html', context)


#Преподаватели

def teacher_list(request):
    """Список всех преподавателей"""
    teachers = Teacher.objects.all()
    return render(request, 'schedule/teacher_list.html', {'teachers': teachers})


def teacher_detail(request, teacher_id):
    """Детальная информация о преподавателе"""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    courses = teacher.courses.all()

    # Проверяем наличие профиля
    try:
        teacher_info = teacher.info
    except TeacherInfo.DoesNotExist:
        teacher_info = None

    context = {
        'teacher': teacher,
        'courses': courses,
        'teacher_info': teacher_info,
    }
    return render(request, 'schedule/teacher_detail.html', context)


def teacher_create(request):
    """Создание нового преподавателя"""
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            Teacher.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                specialization=form.cleaned_data.get('specialization', ''),
                experience_years=form.cleaned_data['experience_years']
            )
            return redirect('teacher_list')
        # Форма невалидна — отображаем с ошибками
        return render(request, 'schedule/teacher_form.html', {'form': form})

    # GET-запрос — пустая форма
    form = TeacherForm()
    return render(request, 'schedule/teacher_form.html', {'form': form})


def teacher_update(request, teacher_id):
    """Обновление информации о преподавателе"""
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        teacher.first_name = request.POST['first_name']
        teacher.last_name = request.POST['last_name']
        teacher.email = request.POST['email']
        teacher.phone = request.POST['phone']
        teacher.specialization = request.POST.get('specialization', '')
        teacher.experience_years = request.POST.get('experience_years', 0)
        teacher.save()
        return redirect('teacher_detail', teacher_id=teacher.id)

    return render(request, 'schedule/teacher_form.html', {'teacher': teacher})


def teacher_delete(request, teacher_id):
    """Удаление преподавателя"""
    teacher = get_object_or_404(Teacher, id=teacher_id)

    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')

    return render(request, 'schedule/teacher_confirm_delete.html', {'teacher': teacher})


#Курсы

def course_list(request):
    """Список всех курсов с фильтрацией по преподавателю"""
    courses = Course.objects.all()
    teacher_id = request.GET.get('teacher')

    if teacher_id:
        courses = courses.filter(teacher_id=teacher_id)

    teachers = Teacher.objects.all()

    context = {
        'courses': courses,
        'teachers': teachers,
        'selected_teacher': teacher_id,
    }
    return render(request, 'schedule/course_list.html', context)


def course_detail(request, course_id):
    """Детальная информация о курсе"""
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(enrollments__course=course)

    context = {
        'course': course,
        'students': students,
        'students_count': students.count(),
    }
    return render(request, 'schedule/course_detail.html', context)


def course_create(request):
    """Создание нового курса"""
    if request.method == 'POST':
        course = Course.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            teacher_id=request.POST.get('teacher') or None,
            level=request.POST['level'],
            duration_weeks=request.POST['duration_weeks'],
            price=request.POST['price'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            max_students=request.POST['max_students']
        )
        return redirect('schedule_course_list')

    teachers = Teacher.objects.all()
    return render(request, 'schedule/course_form.html', {'teachers': teachers})


def course_update(request, course_id):
    """Обновление информации о курсе"""
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course.title = request.POST['title']
        course.description = request.POST['description']
        course.teacher_id = request.POST.get('teacher') or None
        course.level = request.POST['level']
        course.duration_weeks = request.POST['duration_weeks']
        course.price = request.POST['price']
        course.start_date = request.POST['start_date']
        course.end_date = request.POST['end_date']
        course.max_students = request.POST['max_students']
        course.save()
        return redirect('schedule_course_detail', course_id=course.id)

    teachers = Teacher.objects.all()
    return render(request, 'schedule/course_form.html', {
        'course': course,
        'teachers': teachers
    })


def course_delete(request, course_id):
    """Удаление курса"""
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course.delete()
        return redirect('schedule_course_list')

    return render(request, 'schedule/course_confirm_delete.html', {'course': course})


# Студенты

def student_list(request):
    """Список всех студентов"""
    students = Student.objects.all()
    return render(request, 'schedule/student_list.html', {'students': students})


def student_detail(request, student_id):
    """Детальная информация о студенте"""
    student = get_object_or_404(Student, id=student_id)
    enrollments = student.enrollments.select_related('course').all()

    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'schedule/student_detail.html', context)


def student_create(request):
    """Создание нового студента"""
    if request.method == 'POST':
        student = Student.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            phone=request.POST.get('phone', ''),
            birth_date=request.POST.get('birth_date') or None,
            status=request.POST['status']
        )
        return redirect('student_list')

    return render(request, 'schedule/student_form.html')


def student_update(request, student_id):
    """Обновление информации о студенте"""
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        student.first_name = request.POST['first_name']
        student.last_name = request.POST['last_name']
        student.email = request.POST['email']
        student.phone = request.POST.get('phone', '')
        student.birth_date = request.POST.get('birth_date') or None
        student.status = request.POST['status']
        student.save()
        return redirect('student_detail', student_id=student.id)

    return render(request, 'schedule/student_form.html', {'student': student})


def student_delete(request, student_id):
    """Удаление студента"""
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        student.delete()
        return redirect('student_list')

    return render(request, 'schedule/student_confirm_delete.html', {'student': student})


# Запись на курсы

def enroll_student(request):
    """Запись студента на курс"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        if not student_id or not course_id:
            return render(request, 'schedule/enroll_form.html', {
                'students': Student.objects.all(),
                'courses': Course.objects.all(),
                'error': 'Выберите студента и курс'
            })

        # Проверяем, не записан ли уже студент
        enrollment, created = Enrollment.objects.get_or_create(
            student_id=student_id,
            course_id=course_id,
            defaults={'status': 'enrolled'}
        )

        if created:
            # Новая запись создана
            return redirect('student_detail', student_id=student_id)
        else:
            # Уже был записан
            return render(request, 'schedule/enroll_form.html', {
                'students': Student.objects.all(),
                'courses': Course.objects.all(),
                'error': 'Студент уже записан на этот курс'
            })

    # GET запрос - показываем форму
    students = Student.objects.all()
    courses = Course.objects.all()

    # Если передан student_id в GET параметрах, выбираем его
    selected_student = request.GET.get('student_id')

    context = {
        'students': students,
        'courses': courses,
        'selected_student': selected_student,
    }
    return render(request, 'schedule/enroll_form.html', context)

def unenroll_student(request, enrollment_id):
    """Отписка студента от курса"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        student_id = enrollment.student.id
        enrollment.delete()
        return redirect('student_detail', student_id=student_id)

    return render(request, 'schedule/unenroll_confirm.html', {'enrollment': enrollment})