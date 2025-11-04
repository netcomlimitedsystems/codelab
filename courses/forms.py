from django import forms
from .models import Course, Lesson, Category, Instructor
from .models import (
    Assignment, MultipleChoiceQuestion, CodeQuestion, TextQuestion,
    MultipleChoiceSubmission, CodeSubmission, TextSubmission
)

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'order', 'content', 'video_url', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter lesson title'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control editor-content',
                'rows': '20',
                'placeholder': 'Write your lesson content here...'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/video'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Estimated duration in minutes'
            }),
        }
        labels = {
            'title': 'Lesson Title',
            'order': 'Lesson Order',
            'content': 'Lesson Content',
            'video_url': 'Video URL',
            'duration_minutes': 'Duration (minutes)',
        }
        help_texts = {
            'order': 'Position of this lesson in the course sequence',
            'video_url': 'Optional: Add a video URL (YouTube, Vimeo, etc.)',
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'difficulty', 'thumbnail', 'duration_hours']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# UPDATED: Assignment forms for multiple questions
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'assignment_type', 'points', 'due_date', 'order', 'is_published']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class MultipleChoiceQuestionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'points', 'explanation', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'option_a': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option D'}),
            'explanation': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'question_text': 'Question',
            'points': 'Points',
            'order': 'Question Order',
        }

class CodeQuestionForm(forms.ModelForm):
    test_cases_json = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6, 
            'class': 'form-control',
            'placeholder': 'Enter test cases as JSON array: [{"input": "1 2", "expected_output": "3", "points": 1}]'
        }),
        required=False,
        help_text="Enter test cases as JSON array"
    )

    class Meta:
        model = CodeQuestion
        fields = ['question_text', 'language', 'starter_code', 'points', 'timeout_seconds', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Describe the coding problem...'
            }),
            'starter_code': forms.Textarea(attrs={
                'rows': 8, 
                'class': 'form-control code-editor',
                'spellcheck': 'false'
            }),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'timeout_seconds': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'question_text': 'Problem Statement',
            'points': 'Points',
            'order': 'Question Order',
        }

class TextQuestionForm(forms.ModelForm):
    class Meta:
        model = TextQuestion
        fields = ['question_text', 'expected_answer', 'points', 'max_length', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Enter the question...'
            }),
            'expected_answer': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Expected answer for auto-grading (optional)'
            }),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'max_length': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'question_text': 'Question',
            'points': 'Points',
            'order': 'Question Order',
        }

class MultipleChoiceSubmissionForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceSubmission
        fields = ['selected_answer']
        widgets = {
            'selected_answer': forms.RadioSelect(attrs={'class': 'form-check-input'})
        }

class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = CodeSubmission
        fields = ['code', 'language']
        widgets = {
            'code': forms.Textarea(attrs={
                'rows': 15, 
                'class': 'form-control code-editor', 
                'spellcheck': 'false'
            }),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }

class TextSubmissionForm(forms.ModelForm):
    class Meta:
        model = TextSubmission
        fields = ['answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'rows': 6,
                'class': 'form-control'
            }),
        }