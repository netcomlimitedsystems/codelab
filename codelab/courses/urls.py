from django.urls import path
from . import views

app_name = "courses"
from django.http import JsonResponse

def dummy_tracker(request):
    return JsonResponse({"status": "ignored"})

urlpatterns = [
    path("hybridaction/zybTrackerStatisticsAction", dummy_tracker),
    path("", views.course_list, name="course_list"),
    path("my-courses/", views.my_courses, name="my_courses"),
    path("catalog/", views.catalog, name="catalog"),

    # Certificates
    path("certificates/", views.my_certificates, name="my_certificates"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    # Certificates
    path("certificate/<int:pk>/", views.view_certificate, name="view_certificate"),
    path("certificate/<int:pk>/download/", views.download_certificate, name="download_certificate"),

    # Lessons
    path("<slug:course_slug>/lesson/<slug:lesson_slug>/", views.lesson_detail, name="lesson_detail"),
    
    path('courses/<int:course_id>/submit_review/', views.submit_review, name='submit_review'),

    # Assignments
    path("<slug:course_slug>/assignment/<int:assignment_id>/", views.assignment_detail, name="assignment_detail"),

    # Exams
    path("<slug:course_slug>/exam/<int:exam_id>/", views.exam_detail, name="exam_detail"),

    # Enrollment
    path("<slug:course_slug>/enroll/", views.enroll_course, name="enroll_course"),

    # Paid enrollment simulation
    path("<slug:course_slug>/pay/", views.pay_course, name="pay_course"),


    path('course/<slug:course_slug>/lesson/<slug:lesson_slug>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),

]
