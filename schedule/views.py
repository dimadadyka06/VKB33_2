from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.http import HttpResponseNotFound

from .forms import TeacherForm, CourseForm, StudentForm
from .models import Teacher, TeacherInfo, Course, Student, Enrollment


# ── ГЛАВНАЯ ─────────────────────────────────────────────────────────────

def index(request):
    context = {
        'teachers_count': Teacher.objects.count(),
        'courses_count': Course.objects.count(),
        'students_count': Student.objects.count(),
        'enrollments_count': Enrollment.objects.count(),
    }
    return render(request, 'schedule/index.html', context)


# ── ПРЕПОДАВАТЕЛИ ────────────────────────────────────────────────────────

def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'schedule/teacher_list.html', {'teachers': teachers})


def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    courses = teacher.courses.all()
    try:
        teacher_info = teacher.info
    except TeacherInfo.DoesNotExist:
        teacher_info = None
    return render(request, 'schedule/teacher_detail.html', {
        'teacher': teacher,
        'courses': courses,
        'teacher_info': teacher_info,
    })


def teacher_create(request):
    """Создание нового преподавателя через ModelForm."""
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'schedule/teacher_form.html', {'form': form})


def teacher_update(request, teacher_id):
    """Редактирование преподавателя через ModelForm."""
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher_detail', teacher_id=teacher.id)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'schedule/teacher_form.html', {
        'form': form,
        'teacher': teacher,
    })


def teacher_delete(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        teacher.delete()
        return redirect('teacher_list')
    return render(request, 'schedule/teacher_confirm_delete.html', {'teacher': teacher})


# ── КУРСЫ ────────────────────────────────────────────────────────────────

def course_list(request):
    courses = Course.objects.all()
    teacher_id = request.GET.get('teacher')
    if teacher_id:
        courses = courses.filter(teacher_id=teacher_id)
    return render(request, 'schedule/course_list.html', {
        'courses': courses,
        'teachers': Teacher.objects.all(),
        'selected_teacher': teacher_id,
    })


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(enrollments__course=course)
    return render(request, 'schedule/course_detail.html', {
        'course': course,
        'students': students,
        'students_count': students.count(),
    })


def course_create(request):
    """Создание нового курса через ModelForm."""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schedule_course_list')
    else:
        form = CourseForm()
    return render(request, 'schedule/course_form.html', {'form': form})


def course_update(request, course_id):
    """Редактирование курса через ModelForm."""
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('schedule_course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'schedule/course_form.html', {
        'form': form,
        'course': course,
    })


def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('schedule_course_list')
    return render(request, 'schedule/course_confirm_delete.html', {'course': course})


# ── СТУДЕНТЫ ─────────────────────────────────────────────────────────────

def student_list(request):
    students = Student.objects.all()
    return render(request, 'schedule/student_list.html', {'students': students})


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    enrollments = student.enrollments.select_related('course').all()
    return render(request, 'schedule/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
    })


def student_create(request):
    """Создание нового студента через ModelForm."""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'schedule/student_form.html', {'form': form})


def student_update(request, student_id):
    """Редактирование студента через ModelForm."""
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_detail', student_id=student.id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'schedule/student_form.html', {
        'form': form,
        'student': student,
    })


def student_delete(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'schedule/student_confirm_delete.html', {'student': student})


# ── ЗАПИСЬ НА КУРСЫ ──────────────────────────────────────────────────────

def enroll_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        if not student_id or not course_id:
            return render(request, 'schedule/enroll_form.html', {
                'students': Student.objects.all(),
                'courses': Course.objects.all(),
                'error': 'Выберите студента и курс',
            })
        enrollment, created = Enrollment.objects.get_or_create(
            student_id=student_id, course_id=course_id,
            defaults={'status': 'enrolled'}
        )
        if created:
            return redirect('student_detail', student_id=student_id)
        return render(request, 'schedule/enroll_form.html', {
            'students': Student.objects.all(),
            'courses': Course.objects.all(),
            'error': 'Студент уже записан на этот курс',
        })
    return render(request, 'schedule/enroll_form.html', {
        'students': Student.objects.all(),
        'courses': Course.objects.all(),
        'selected_student': request.GET.get('student_id'),
    })


def unenroll_student(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    if request.method == 'POST':
        student_id = enrollment.student.id
        enrollment.delete()
        return redirect('student_detail', student_id=student_id)
    return render(request, 'schedule/unenroll_confirm.html', {'enrollment': enrollment})
