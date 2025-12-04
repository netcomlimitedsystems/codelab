from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files import File
from community.models import Tag
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from django.core.files.base import ContentFile
def generate_pdf(self):
    """
    Generates a PDF for the exam and returns it as a Django File
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Exam: {self.title}")

    c.setFont("Helvetica", 12)
    y = height - 100
    for i, question in enumerate(self.questions.all(), start=1):
        c.drawString(50, y, f"{i}. {question.question_text}")
        y -= 20
        c.drawString(70, y, f"A. {question.choice_a}")
        y -= 15
        c.drawString(70, y, f"B. {question.choice_b}")
        y -= 15
        c.drawString(70, y, f"C. {question.choice_c}")
        y -= 15
        c.drawString(70, y, f"D. {question.choice_d}")
        y -= 25

        if y < 100:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return ContentFile(buffer.getvalue(), name=f"{self.slug}-exam.pdf")

User = get_user_model()

LEVEL_CHOICES = (
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
)

PAYMENT_METHODS = (
    ("mpesa", "M-Pesa"),
    ("paypal", "PayPal"),
    ("stripe", "Stripe"),
    ("manual", "Manual / Bank Transfer"),
)


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    short_description = models.CharField(max_length=400, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=120, blank=True)
    tag = models.ForeignKey(Tag,related_name='tags',on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    featured = models.BooleanField(default=False)
    payment_methods = models.JSONField(default=list, blank=True)  # store allowed payment types (e.g. ["mpesa","paypal"])
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ("-featured", "-created_at")
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"slug": self.slug})

    def is_free(self):
        """Return True if course is free (price empty/zero or is_paid False)."""
        return not self.is_paid or (self.price is None or self.price <= 0)

    def get_payment_methods_display(self):
        """Return human-readable list of configured payment methods."""
        method_map = dict(PAYMENT_METHODS)
        return [method_map.get(m, str(m)) for m in self.payment_methods]

from django.utils.text import slugify

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True, null=True)
    attachment = models.FileField(upload_to="lessons/attachments/", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ("order",)
        unique_together = (("course", "slug"),)
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



class Assignment(models.Model):
    course = models.ForeignKey(Course, related_name="assignments", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.PositiveIntegerField(default=100)
    allow_file_upload = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return f"{self.course.title} — {self.title}"
    def get_absolute_url(self):
        return reverse('courses:assignment_detail', kwargs={
            'course_slug': self.course.slug,
            'assignment_id': self.id
        })

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, related_name="submissions", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="assignment_submissions", on_delete=models.CASCADE)
    file = models.FileField(upload_to="assignments/submissions/", null=True, blank=True)
    text_answer = models.TextField(blank=True)
    score = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(default=timezone.now)
    graded = models.BooleanField(default=False)

    class Meta:
        unique_together = (("assignment", "student"),)
        verbose_name = "Assignment Submission"
        verbose_name_plural = "Assignment Submissions"

    def __str__(self):
        return f"{self.assignment.title} — {self.student.username}"


class Exam(models.Model):
    course = models.ForeignKey(Course, related_name="exams", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField(default=60)
    pass_mark = models.PositiveIntegerField(default=50)  # percent
    is_active = models.BooleanField(default=True)
    scheduled_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    def get_absolute_url(self):
        return reverse("courses:exam_detail", kwargs={
            "course_slug": self.course.slug,
            "exam_id": self.id
        })



class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    question_text = models.TextField()
    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    choice_d = models.CharField(max_length=255)
    correct_choice = models.CharField(max_length=1, choices=(("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")))
    points = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Exam Question"
        verbose_name_plural = "Exam Questions"

    def __str__(self):
        return f"{self.exam.title} — {self.question_text[:50]}"


class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, related_name="submissions", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="exam_submissions", on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(default=timezone.now)
    passed = models.BooleanField(default=False)

    class Meta:
        unique_together = (("exam", "student"),)
        verbose_name = "Exam Submission"
        verbose_name_plural = "Exam Submissions"

    def __str__(self):
        return f"{self.exam.title} — {self.student.username}"


class Enrollment(models.Model):
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    student = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("course", "student"),)
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.student.username} — {self.course.title}"


class Certificate(models.Model):
    user = models.ForeignKey(User, related_name="certificates", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="certificates", on_delete=models.CASCADE)
    issued_at = models.DateTimeField(default=timezone.now)
    cert_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to="certificates/qr_codes/", null=True, blank=True)
    file = models.FileField(upload_to="certificates/files/", null=True, blank=True)  # generated PDF
    issued_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "course"),)
        ordering = ("-issued_at",)
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"Certificate: {self.user.username} — {self.course.title}"

    # Generate QR code
    def generate_qr(self):
        payload = f"codelab://certificate/{self.cert_id}"
        img = qrcode.make(payload)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"cert-{self.cert_id}.png"
        filebuffer = ContentFile(buffer.getvalue())
        self.qr_code.save(filename, filebuffer, save=False)
        buffer.close()

    # Generate PDF Certificate
    def generate_pdf(self):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(600, 400))

        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(300, 350, "Certificate of Completion")

        c.setFont("Helvetica", 18)
        # Get full name from profile, fallback to username
        if hasattr(self.user, "profile") and getattr(self.user.profile, "full_name", ""):
            full_name = self.user.profile.full_name
        else:
            full_name = self.user.get_full_name() or self.user.username

        c.drawCentredString(300, 300, f"Presented to: {full_name}")
        c.drawCentredString(300, 250, "For successfully completing the course:")

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(300, 200, f"{self.course.title}")

        c.setFont("Helvetica", 14)
        c.drawCentredString(300, 150, f"Issued on: {self.issued_at.strftime('%d %B %Y')}")

        c.showPage()
        c.save()
        buffer.seek(0)
        filename = f"certificate-{self.cert_id}.pdf"
        self.file.save(filename, File(buffer), save=False)
        buffer.close()

    # Save override: QR + PDF
    def save(self, *args, **kwargs):
        if not self.qr_code:
            try:
                self.generate_qr()
            except Exception:
                pass
        if not self.file:
            try:
                self.generate_pdf()
            except Exception:
                pass
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)  # Optional link to course/exam
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
class LessonCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
        verbose_name = 'Lesson Completion'
        verbose_name_plural = 'Lesson Completions'
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"
class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
