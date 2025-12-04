from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView, CustomPasswordChangeDoneView

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('terms/',views.terms_and_conditions,name='terms_and_conditions'),
    path('privacy/',views.privacy,name='privacy'),
    # Custom password change URLs with our views
    path('password-change/', CustomPasswordChangeView.as_view(),name='password_change'),
    path('password-change-done/',CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('sessions/', views.sessions, name='sessions'),
    path('two-factor/setup/', views.two_factor_setup, name='two_factor_setup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]

