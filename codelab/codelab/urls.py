from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from courses.admin import ExamAdmin
from courses.models import Exam
urlpatterns = [
    # path('admin/exams/exam/add-quick/', admin.site.admin_view(ExamAdmin(Exam, admin.site).add_quick_view),name='exam_add_quick'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),  # adds social login URLs
    path('courses/', include('courses.urls')),
    path('community/', include('community.urls')),
    path('', include('core.urls')),  # Your main app
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
