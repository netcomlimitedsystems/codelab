from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('certify/',views.get_certify,name='get_certify'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_pk>/lesson/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/create/', views.create_course, name='create_course'),
    path('instructor/edit/<int:pk>/', views.edit_course, name='edit_course'),  
    path('course/<int:course_pk>/delete/', views.delete_course, name='delete_course'),
    path('<int:course_pk>/complete/', views.complete_course, name='complete_course'),
    path('certificate/<int:pk>/', views.certificate_view, name='certificate'),
    path('<int:course_pk>/lesson/<int:lesson_pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('<int:pk>/certificate/download/', views.download_certificate, name='download_certificate'),
    path('course/<int:course_id>/certificate/pdf/', views.generate_certificate_pdf, name='generate_certificate_pdf'),
    path('course/<int:course_pk>/lesson/create/', views.create_lesson, name='create_lesson'),
    path('course/<int:course_pk>/lesson/<int:lesson_pk>/edit/', views.edit_lesson, name='edit_lesson'),
    path('course/<int:course_pk>/lessons/', views.manage_lessons, name='manage_lessons'),
    path('lesson/create/quick/', views.create_lesson_quick, name='create_lesson_quick'),
    path('course/<int:course_pk>/lesson/<int:lesson_pk>/delete/', views.delete_lesson, name='delete_lesson'),
    path('lessons/update-order/', views.update_lesson_order, name='update_lesson_order'),
    
    # Assignment URLs
    path('course/<int:course_pk>/assignments/', views.assignment_list, name='assignment_list'),
    path('course/<int:course_pk>/assignment/<int:assignment_pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:assignment_pk>/submissions/', views.view_submissions, name='view_submissions'),  
    path('assignment/<int:assignment_id>/add-question/',views.add_question,name='add_question'),
    path('course/<int:course_pk>/assignment/<int:assignment_pk>/edit/', views.edit_assignment, name='edit_assignment'),
    path('course/<int:course_pk>/assignment/<int:assignment_pk>/delete/', views.delete_assignment, name='delete_assignment'),

    # Instructor assignment management
    path('course/<int:course_pk>/assignments/manage/', views.manage_assignments, name='manage_assignments'),
    path('course/<int:course_pk>/assignment/create/', views.create_assignment, name='create_assignment'),
    
    # Assignment question management
    path('assignment/<int:assignment_pk>/manage-questions/', views.manage_assignment_questions, name='manage_assignment_questions'),
    path('assignment/<int:assignment_pk>/add-multiple-choice/', views.add_multiple_choice_question, name='add_multiple_choice'),
    path('assignment/<int:assignment_pk>/add-code-question/', views.add_code_question, name='add_code_question'),
    path('assignment/<int:assignment_pk>/add-text-question/', views.add_text_question, name='add_text_question'),
]