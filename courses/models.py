from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
from users.models import UserProfile


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_picture = models.ImageField(upload_to='instructors/', blank=True)
    
    def __str__(self):
        return self.user.get_full_name()

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    duration_hours = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'course']

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']

class CourseCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=100, unique=True)
    grade = models.CharField(max_length=10, default='A+')
    final_score = models.DecimalField(max_digits=5, decimal_places=2, default=98.00)
    
    class Meta:
        unique_together = ['user', 'course']

class Assignment(models.Model):
    ASSIGNMENT_TYPES = [
        ('mixed', 'Mixed Questions'),
        ('multiple_choice', 'Multiple Choice Only'),
        ('code', 'Code Questions Only'),
        ('text', 'Text Questions Only'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='mixed')
    points = models.PositiveIntegerField(default=10)
    due_date = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_questions = models.PositiveIntegerField(default=10)  


    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_question_count(self):
        """Get total number of questions"""
        return (
            self.multiplechoicequestion_questions.count() +
            self.codequestion_questions.count() +
            self.textquestion_questions.count()
        )

    def get_total_points(self):
        """Calculate total points from all questions"""
        total = 0
        total += self.multiplechoicequestion_questions.aggregate(total=Sum('points'))['total'] or 0
        total += self.codequestion_questions.aggregate(total=Sum('points'))['total'] or 0
        total += self.textquestion_questions.aggregate(total=Sum('points'))['total'] or 0
        return total



class BaseQuestion(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='%(class)s_questions')
    question_text = models.TextField()
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return self.question_text[:50]


class MultipleChoiceQuestion(BaseQuestion):
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ['order']


class CodeQuestion(BaseQuestion):
    LANGUAGES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('c', 'C'),
    ]
    
    language = models.CharField(max_length=20, choices=LANGUAGES, default='python')
    starter_code = models.TextField(blank=True)
    test_cases = models.JSONField(default=list)
    solution_code = models.TextField(blank=True)
    timeout_seconds = models.IntegerField(default=10)

    class Meta:
        ordering = ['order']


class TextQuestion(BaseQuestion):
    expected_answer = models.TextField(blank=True)
    max_length = models.PositiveIntegerField(default=500)

    class Meta:
        ordering = ['order']

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_score = models.FloatField(default=0)
    is_completed = models.BooleanField(default=False)
    time_taken_minutes = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['assignment', 'user']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} - {self.assignment.title}"

    def calculate_total_score(self):
        """Calculate total score from all question submissions"""
        mc_score = self.mc_submissions.aggregate(total=Sum('score'))['total'] or 0
        code_score = self.code_submissions.aggregate(total=Sum('score'))['total'] or 0
        text_score = self.text_submissions.aggregate(total=Sum('score'))['total'] or 0
        return mc_score + code_score + text_score


class BaseQuestionSubmission(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE, related_name='%(class)s_submissions')
    question = models.ForeignKey('%(class)sQuestion', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.submission.user.username} - {self.question.id}"


class MultipleChoiceSubmission(BaseQuestionSubmission):
    question = models.ForeignKey(MultipleChoiceQuestion, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])


class CodeSubmission(BaseQuestionSubmission):
    question = models.ForeignKey(CodeQuestion, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=20)
    execution_result = models.JSONField(default=dict)


class TextSubmission(BaseQuestionSubmission):
    question = models.ForeignKey(TextQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()