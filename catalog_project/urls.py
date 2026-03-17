from django.contrib import admin
from django.urls import path, include
from catalog import views as catalog_views
from schedule import views as schedule_views

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    
    # ===== catalog (публичная часть) =====
    path('', catalog_views.index, name='index'),
    path('courses/', catalog_views.courses, name='courses'),
    path('courses/<int:course_id>/', catalog_views.course_detail, name='course_detail'),
    path('authors/', catalog_views.authors, name='authors'),
    path('authors/<int:author_id>/', catalog_views.author_details, name='author_details'),
    path('info/', catalog_views.info, name='info'),
    
    # ===== schedule (управление) =====
    # Главная schedule
    path('schedule/', schedule_views.index, name='schedule_index'),
    
    # Teachers
    path('schedule/teachers/', schedule_views.teacher_list, name='teacher_list'),
    path('schedule/teachers/<int:teacher_id>/', schedule_views.teacher_detail, name='teacher_detail'),
    path('schedule/teachers/create/', schedule_views.teacher_create, name='teacher_create'),
    path('schedule/teachers/<int:teacher_id>/update/', schedule_views.teacher_update, name='teacher_update'),
    path('schedule/teachers/<int:teacher_id>/delete/', schedule_views.teacher_delete, name='teacher_delete'),
    
    # Courses
    path('schedule/courses/', schedule_views.course_list, name='schedule_course_list'),
    path('schedule/courses/<int:course_id>/', schedule_views.course_detail, name='schedule_course_detail'),
    path('schedule/courses/create/', schedule_views.course_create, name='course_create'),
    path('schedule/courses/<int:course_id>/update/', schedule_views.course_update, name='course_update'),
    path('schedule/courses/<int:course_id>/delete/', schedule_views.course_delete, name='course_delete'),
    
    # Students
    path('schedule/students/', schedule_views.student_list, name='student_list'),
    path('schedule/students/<int:student_id>/', schedule_views.student_detail, name='student_detail'),
    path('schedule/students/create/', schedule_views.student_create, name='student_create'),
    path('schedule/students/<int:student_id>/update/', schedule_views.student_update, name='student_update'),
    path('schedule/students/<int:student_id>/delete/', schedule_views.student_delete, name='student_delete'),
    
    # Enrollment (запись/отписка)
    path('schedule/enroll/', schedule_views.enroll_student, name='enroll_student'),
    path('schedule/unenroll/<int:enrollment_id>/', schedule_views.unenroll_student, name='unenroll_student'),
]

# Обработчик 404
handler404 = 'catalog.views.not_found'