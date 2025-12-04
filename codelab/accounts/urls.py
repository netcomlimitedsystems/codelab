from django.urls import path
from . import views

app_name = "accounts"
from django.http import JsonResponse

def dummy_tracker(request):
    return JsonResponse({"status": "ignored"})

urlpatterns = [
    path("hybridaction/zybTrackerStatisticsAction", dummy_tracker),
    # Authentication & Core
    path('',views.home,name='home'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("register/", views.register, name="register"),
    path("verify/<str:token>/", views.verify_email, name="verify_email"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("login_redirect/", views.login_redirect, name="login_redirect"),
    path("update_profile/", views.update_profile, name="update_profile"),
    path('notification/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/fetch/', views.fetch_unread_notifications, name='fetch_unread_notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('change-password/', views.change_password, name='change_password'),
    path("settings/profile/", views.profile_setting, name="profile_settings"),
    path("accept-terms/", views.accept_terms, name="accept_terms"),
    path('upgrade/', views.upgrade_account, name='upgrade'),
    path('courses/bulk-action/', views.course_bulk_action, name='course_bulk_action'),

    # Static Pages
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("support/", views.support, name="support"),
    path("contact/", views.contact, name="contact"),

    # Career
    path("careers/", views.career_list, name="career_list"),
    path("careers/page/<int:page>/", views.career_list, name="career_list_paginated"),
    path("careers/<slug:slug>/", views.career_detail, name="career_detail"),

    # Blog
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/page/<int:page>/", views.blog_list, name="blog_list_paginated"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path('search/', views.blog_search, name='blog_search'),  # <-- add this
    path('subscribe/', views.subscribe, name='subscribe'),  # <-- add this
    path('newsletter-subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),  # <-- add this
    path('contribute/', views.contribute, name='contribute'),  # <-- add this
    path('blog/category/<slug:slug>/', views.blog_category, name='blog_category'),  # <--- THIS

    # Blog Comments
    path("blog/<slug:slug>/comment/", views.add_comment, name="add_comment"),

    # ----------------------------
    # USER MANAGEMENT
    # ----------------------------
    path("users/", views.admin_user_list, name="admin_user_list"),
    path("users/add/", views.admin_user_add, name="admin_user_add"),
    path("users/<int:user_id>/edit/", views.admin_user_edit, name="admin_user_edit"),
    path("users/<int:user_id>/delete/", views.admin_user_delete, name="admin_user_delete"),

    # ----------------------------
    # COURSES
    # ----------------------------
    path('courses/detail/', views.admin_course_detail, name='course_detail'),
    path("courses/", views.admin_course_list, name="course_list"),
    path("courses/add/", views.admin_course_add, name="course_add"),
    path("courses/<int:course_id>/edit/", views.admin_course_edit, name="course_edit"),
    path("courses/<int:course_id>/delete/", views.admin_course_delete, name="course_delete"),

    # ----------------------------
    # LESSONS
    # ----------------------------
    path("courses/<int:course_id>/lessons/", views.admin_lesson_list, name="lesson_list"),
    path("courses/<int:course_id>/lessons/add/", views.admin_lesson_add, name="lesson_add"),
    path("lessons/<int:lesson_id>/edit/", views.admin_lesson_edit, name="lesson_edit"),
    path("lessons/<int:lesson_id>/delete/", views.admin_lesson_delete, name="lesson_delete"),
    path("lessons/all/", views.admin_lesson_list_all, name="admin_lesson_list_all"),
    path("lessons/quick-add/", views.admin_lesson_add_quick, name="admin_lesson_add_quick"),

    # ----------------------------
    # ASSIGNMENTS
    # ----------------------------
    path("courses/<int:course_id>/assignments/", views.admin_assignment_list, name="assignment_list"),
    path("courses/<int:course_id>/assignments/add/", views.admin_assignment_add, name="assignment_add"),
    path("assignments/<int:assignment_id>/edit/", views.admin_assignment_edit, name="assignment_edit"),
    path("assignments/<int:assignment_id>/delete/", views.admin_assignment_delete, name="assignment_delete"),
    path("assignments/all/", views.admin_assignment_list_all, name="admin_assignment_list_all"),
    path("assignments/quick-add/", views.admin_assignment_add_quick, name="admin_assignment_add_quick"),

    # ----------------------------
    # EXAMS
    # ----------------------------
    path("courses/<int:course_id>/exams/", views.admin_exam_list, name="exam_list"),
    path("courses/<int:course_id>/exams/add/", views.admin_exam_add, name="exam_add"),
    path("exams/<int:exam_id>/edit/", views.admin_exam_edit, name="exam_edit"),
    path("exams/<int:exam_id>/delete/", views.admin_exam_delete, name="exam_delete"),
    path("exams/all/", views.admin_exam_list_all, name="admin_exam_list_all"),
    path("exams/quick-add/", views.admin_exam_add_quick, name="admin_exam_add_quick"),
    path('exam/create/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    

    # ----------------------------
    # CERTIFICATES
    # ----------------------------
    path("certificates/", views.admin_certificate_list, name="admin_certificate_list"),
    path("certificates/<int:certificate_id>/delete/", views.admin_certificate_delete, name="admin_certificate_delete"),

    # Notifications
    path('mark_notification_read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('fetch_unread_notifications/', views.fetch_unread_notifications, name='fetch_unread_notifications'),
    path('mark_all_notifications_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    path("mfa/setup/", views.mfa_setup, name="mfa_setup"),
    path("mfa/verify/", views.mfa_verify, name="mfa_verify"),  # <-- ADD THIS
    path("security/", views.security_settings, name="security_settings"),

]