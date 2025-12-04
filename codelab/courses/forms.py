from django import forms
from .models import Course, Lesson, Assignment, Exam, ExamQuestion

# ----------------------------
# COURSE FORM
# ----------------------------
class CourseForm(forms.ModelForm):
    payment_methods = forms.MultipleChoiceField(
        choices=[
            ("mpesa", "M-Pesa"),
            ("paypal", "PayPal"),
            ("stripe", "Stripe"),
            ("manual", "Manual / Bank Transfer"),
        ],
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Course
        fields = [
            "title",
            "slug",
            "short_description",
            "description",
            "category",
            "level",
            "is_paid",
            "price",
            "featured",
            "payment_methods",
            "thumbnail",
            "published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "short_description": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "is_paid": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ----------------------------
# LESSON FORM
# ----------------------------
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "slug",
            "content",
            "order",
            "video_url",
            "attachment",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


# ----------------------------
# ASSIGNMENT FORM
# ----------------------------
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            "title",
            "description",
            "due_date",
            "max_score",
            "allow_file_upload",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "max_score": forms.NumberInput(attrs={"class": "form-control"}),
            "allow_file_upload": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# ----------------------------
# EXAM FORM
# ----------------------------
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "title",
            "duration_minutes",
            "pass_mark",
            "is_active",
            "scheduled_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "pass_mark": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "scheduled_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }


# ----------------------------
# EXAM QUESTION FORM
# ----------------------------
class ExamQuestionForm(forms.ModelForm):
    class Meta:
        model = ExamQuestion
        fields = [
            "question_text",
            "choice_a",
            "choice_b",
            "choice_c",
            "choice_d",
            "correct_choice",
            "points",
        ]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "choice_a": forms.TextInput(attrs={"class": "form-control"}),
            "choice_b": forms.TextInput(attrs={"class": "form-control"}),
            "choice_c": forms.TextInput(attrs={"class": "form-control"}),
            "choice_d": forms.TextInput(attrs={"class": "form-control"}),
            "correct_choice": forms.Select(attrs={"class": "form-select"}),
            "points": forms.NumberInput(attrs={"class": "form-control"}),
        }
