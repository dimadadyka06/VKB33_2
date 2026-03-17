from django.shortcuts import render, get_object_or_404
from django.http import Http404
from schedule.models import Teacher, Course  # импортируем модели из schedule


def index(request):
    """Главная страница со статистикой"""
    context = {
        'courses_count': Course.objects.count(),
        'teachers_count': Teacher.objects.count(),
    }
    return render(request, 'index.html', context)


def courses(request):
    """Список всех курсов"""
    courses_list = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses_list})


def course_detail(request, course_id):
    """Детальная страница курса"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise Http404("Курс не найден")

    # Получаем преподавателя курса
    teacher = course.teacher

    return render(request, 'course_detail.html', {
        'course': course,
        'teacher': teacher
    })


def authors(request):
    """Список всех преподавателей (авторов курсов)"""
    authors_list = Teacher.objects.all()
    return render(request, 'authors.html', {'authors': authors_list})


def author_details(request, author_id):
    """Детальная страница преподавателя"""
    try:
        author = Teacher.objects.get(id=author_id)
    except Teacher.DoesNotExist:
        raise Http404("Автор не найден")

    # Получаем курсы автора
    courses = author.courses.all()

    return render(request, 'author_details.html', {
        'author': author,
        'courses': courses
    })


def info(request):
    """Страница информации о сайте"""
    return render(request, 'info.html')


def not_found(request, exception=None):
    """Страница 404"""
    return render(request, 'not_found.html', status=404)