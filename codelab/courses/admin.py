from django.contrib import admin
from .models import (
    Course, Lesson, Assignment, AssignmentSubmission, Exam, ExamQuestion,
    ExamSubmission, Enrollment, Certificate, Notification
)

# -----------------------------
# Courses & Lessons
# -----------------------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "is_paid", "price", "featured", "created_at")
    search_fields = ("title", "category", "tag","description")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_paid", "level", "featured")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "created_at")
    search_fields = ("title", "course__title")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("course",)


# -----------------------------
# Assignments
# -----------------------------
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date", "max_score")
    list_filter = ("course",)


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ("assignment", "student", "score", "graded", "submitted_at")
    list_filter = ("assignment__course", "graded")
    search_fields = ("student__username", "assignment__title")


# -----------------------------
# Exams
# -----------------------------
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "duration_minutes", "is_active")
    list_filter = ("course", "is_active")
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        
        custom_urls = [
            path('add-quick/',
                 self.admin_site.admin_view(self.add_quick_view),
                 name='exams_exam_add_quick'),
        ]
        return custom_urls + urls
    
    def add_quick_view(self, request):
        if request.method == 'POST':
            try:
                # Create Exam
                exam = Exam.objects.create(
                    course_id=request.POST.get('course'),
                    title=request.POST.get('title'),
                    duration_minutes=request.POST.get('duration_minutes', 60),
                    pass_mark=request.POST.get('pass_mark', 50),
                    is_active='is_active' in request.POST,
                    scheduled_date=request.POST.get('scheduled_date') or timezone.now()
                )
                
                # Create Questions
                questions_data = []
                for key in request.POST:
                    if key.startswith('questions['):
                        parts = key.split('[')[1].split(']')
                        index = int(parts[0])
                        field = parts[1].replace('[', '').replace(']', '')
                        
                        if len(questions_data) <= index:
                            questions_data.append({})
                        
                        questions_data[index][field] = request.POST[key]
                
                for question_data in questions_data:
                    if question_data.get('question_text'):
                        ExamQuestion.objects.create(
                            exam=exam,
                            question_text=question_data['question_text'],
                            choice_a=question_data['choice_a'],
                            choice_b=question_data['choice_b'],
                            choice_c=question_data['choice_c'],
                            choice_d=question_data['choice_d'],
                            correct_choice=question_data['correct_choice'],
                            points=question_data.get('points', 1)
                        )
                
                messages.success(request, f'Exam "{exam.title}" created successfully with {len(questions_data)} questions.')
                return redirect('admin:exams_exam_changelist')
                
            except Exception as e:
                messages.error(request, f'Error creating exam: {str(e)}')
        
        # Get all courses for the dropdown
        courses = Course.objects.all()
        return render(request, 'admin/exams/exam_add_quick.html', {
            'courses': courses,
            'title': 'Add Quick Exam',
        })


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "question_text", "points")
    search_fields = ("question_text",)


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "score", "passed", "submitted_at")
    list_filter = ("exam__course", "passed")
    search_fields = ("student__username", "exam__title")


# -----------------------------
# Enrollment
# -----------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at")
    list_filter = ("course",)


# -----------------------------
# Certificates
# -----------------------------
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "issued_at", "cert_id")
    readonly_fields = ("issued_at", "cert_id", "qr_code", "file")
    search_fields = ("user__username", "user__profile__full_name", "course__title", "cert_id")


# -----------------------------
# Notifications
# -----------------------------
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    readonly_fields = ("created_at",)
