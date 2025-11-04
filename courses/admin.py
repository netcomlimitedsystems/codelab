from django.contrib import admin
from .models import Category, Course, Lesson, Enrollment, Instructor,LessonProgress
# courses/admin.py
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'completed', 'completed_at']  # Change to 'user'
    list_filter = ['completed', 'enrolled_at', 'course']
    search_fields = ['user__username', 'course__title']  # Change to 'user'
    readonly_fields = ['enrolled_at']

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at', 'last_accessed']  # Change to 'user'
    list_filter = ['completed', 'lesson__course']
    search_fields = ['user__username', 'lesson__title']  # Change to 'user'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'price', 'difficulty', 'is_published', 'created_at']
    list_filter = ['category', 'difficulty', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_published']

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration_minutes']
    list_filter = ['course']
    search_fields = ['title', 'content']

