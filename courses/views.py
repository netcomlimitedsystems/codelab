from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from weasyprint import HTML
import markdown
from datetime import timedelta
import json
from django.db.models import Sum, Avg

from .models import Course, Lesson, Category, Enrollment, Instructor, LessonProgress
from .forms import CourseForm, LessonForm

# Import assignment models and forms
from .models import (
    Assignment, AssignmentSubmission, MultipleChoiceQuestion,
    CodeQuestion, TextQuestion, MultipleChoiceSubmission,
    CodeSubmission, TextSubmission
)
from .forms import (
    AssignmentForm, MultipleChoiceQuestionForm, CodeQuestionForm,
    TextQuestionForm
)
from .services import CodeExecutor


# Certificate Views
@login_required
def generate_certificate_pdf(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    
    # Check if user has completed the course
    if not hasattr(user, 'completed_courses') or not user.completed_courses.filter(id=course_id).exists():
        return HttpResponse("You haven't completed this course yet.", status=403)
    
    html_string = render_to_string('courses/certificate_pdf.html', {
        'user': user,
        'course': course,
    })
    
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()
    
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate-{course.slug}-{user.username}.pdf"'
    
    return response


@login_required
def certificate_view(request, pk):
    course = get_object_or_404(Course, pk=pk)
    user = request.user
    return render(request, 'courses/certificate.html', {'course': course, 'user': user})


@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    
    if not hasattr(user, 'completed_courses') or not user.completed_courses.filter(id=course_id).exists():
        return HttpResponse("You haven't completed this course yet.", status=403)
    
    context = {
        'user': user,
        'course': course,
    }
    
    html_string = render_to_string('courses/certificate_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()
    
    response = HttpResponse(result, content_type='application/pdf')
    filename = f"certificate-{course.slug}-{user.get_full_name().replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# Course Progress Views
@login_required
def complete_course(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'enrolled_at': timezone.now()}
    )
    
    if not enrollment.completed:
        enrollment.completed = True
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        lessons = course.lessons.all()
        for lesson in lessons:
            lesson_progress, created = LessonProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={'completed': True, 'completed_at': timezone.now()}
            )
            if not lesson_progress.completed:
                lesson_progress.completed = True
                lesson_progress.completed_at = timezone.now()
                lesson_progress.save()
        
        messages.success(request, f'Congratulations! You have completed "{course.title}"! 🎉')
    else:
        messages.info(request, f'You have already completed "{course.title}"!')
    
    return redirect('courses:course_detail', pk=course_pk)


@login_required
def mark_lesson_complete(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    
    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True, 'completed_at': timezone.now()}
    )
    
    if not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.completed_at = timezone.now()
        lesson_progress.save()
        messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
    else:
        messages.info(request, f'Lesson "{lesson.title}" is already completed!')
    
    return redirect('courses:lesson_detail', course_pk=course_pk, lesson_pk=lesson_pk)


# Course Display Views
def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('instructor', 'category')
    
    # Apply filters
    search_query = request.GET.get('search')
    category_filter = request.GET.getlist('category')
    difficulty_filter = request.GET.getlist('difficulty')
    price_filter = request.GET.get('price')
    duration_filter = request.GET.get('duration')
    sort_by = request.GET.get('sort', 'recommended')
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructor__user__first_name__icontains=search_query) |
            Q(instructor__user__last_name__icontains=search_query)
        )
    
    if category_filter:
        courses = courses.filter(category_id__in=category_filter)
    
    if difficulty_filter:
        courses = courses.filter(difficulty__in=difficulty_filter)
    
    if price_filter == 'free':
        courses = courses.filter(price=0)
    elif price_filter == 'paid':
        courses = courses.filter(price__gt=0)
    
    if duration_filter == 'short':
        courses = courses.filter(duration_hours__lte=5)
    elif duration_filter == 'medium':
        courses = courses.filter(duration_hours__gt=5, duration_hours__lte=10)
    elif duration_filter == 'long':
        courses = courses.filter(duration_hours__gt=10)
    
    # Sorting
    if sort_by == 'newest':
        courses = courses.order_by('-created_at')
    elif sort_by == 'price_low':
        courses = courses.order_by('price')
    elif sort_by == 'price_high':
        courses = courses.order_by('-price')
    elif sort_by == 'rating':
        courses = courses.order_by('-created_at')
    else:
        courses = courses.order_by('-created_at')
    
    # Add enrollment counts
    for course in courses:
        course.enrollment_count = Enrollment.objects.filter(course=course).count()
        course.average_rating = 4.5
    
    categories = Category.objects.annotate(course_count=Count('course'))
    
    paginator = Paginator(courses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'categories': categories,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    lessons = course.lessons.all().order_by('order')
    
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, 
            course=course
        ).exists()
    
    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}')
    
    return redirect('courses:course_detail', pk=pk)


# Instructor Views
@login_required
def instructor_dashboard(request):
    # Check if user is an instructor
    if not hasattr(request.user, 'instructor'):
        messages.error(request, 'You need to be an instructor to access this page.')
        return redirect('pages:home')
    
    instructor_courses = Course.objects.filter(instructor=request.user.instructor)
    
    # Calculate statistics
    total_students = Enrollment.objects.filter(
        course__in=instructor_courses
    ).values('user').distinct().count()
    
    total_revenue = instructor_courses.aggregate(
        total_revenue=Sum('price')
    )['total_revenue'] or 0
    
    # Assignment statistics
    total_assignments = Assignment.objects.filter(course__in=instructor_courses).count()
    total_submissions = AssignmentSubmission.objects.filter(
        assignment__course__in=instructor_courses
    ).count()
    
    # Assignment type breakdown
    assignment_stats = {
        'multiple_choice': Assignment.objects.filter(
            course__in=instructor_courses, 
            assignment_type='multiple_choice'
        ).count(),
        'code': Assignment.objects.filter(
            course__in=instructor_courses, 
            assignment_type='code'
        ).count(),
        'text': Assignment.objects.filter(
            course__in=instructor_courses, 
            assignment_type='text'
        ).count(),
        'mixed': Assignment.objects.filter(
            course__in=instructor_courses, 
            assignment_type='mixed'
        ).count(),
    }
    
    # Recent assignments
    recent_assignments = Assignment.objects.filter(
        course__in=instructor_courses
    ).select_related('course').order_by('-created_at')[:4]
    
    # Add question counts to recent assignments
    for assignment in recent_assignments:
        assignment.question_count = assignment.get_question_count()
    
    # Get recent students (last 5 enrollments)
    recent_students = Enrollment.objects.filter(
        course__in=instructor_courses
    ).select_related('user', 'course').order_by('-enrolled_at')[:5]
    
    # Calculate enrollment counts for each course first
    course_enrollment_counts = {}
    for course in instructor_courses:
        course_enrollment_counts[course.id] = Enrollment.objects.filter(course=course).count()
    
    # Calculate total possible submissions
    total_possible_submissions = 0
    for course in instructor_courses:
        course_assignments_count = course.assignments.count()
        course_enrollments = course_enrollment_counts[course.id]
        total_possible_submissions += course_assignments_count * course_enrollments
    
    # Calculate submission rate
    submission_rate = (total_submissions / total_possible_submissions * 100) if total_possible_submissions > 0 else 0
    
    # Add calculated fields to each course
    for course in instructor_courses:
        course.enrollment_count = course_enrollment_counts[course.id]
        course.revenue = course.price * course.enrollment_count
        course.average_rating = 4.5  # This would come from reviews
        course.review_count = 12  # This would come from reviews
        # Prefetch assignments count to avoid N+1 queries
        course.assignments_count = course.assignments.count()
    
    # Recent activity (simplified - you can enhance this)
    recent_activity = [
        {
            'title': 'New Student Enrollment',
            'description': 'John Doe enrolled in Python Basics',
            'timestamp': timezone.now() - timedelta(hours=2)
        },
        {
            'title': 'Assignment Submitted',
            'description': 'Sarah completed "Variables and Data Types" assignment',
            'timestamp': timezone.now() - timedelta(hours=5)
        },
        {
            'title': 'Course Completed',
            'description': 'Mike completed Web Development Fundamentals',
            'timestamp': timezone.now() - timedelta(days=1)
        }
    ]
    
    context = {
        'instructor_courses': instructor_courses,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'total_assignments': total_assignments,
        'total_submissions': total_submissions,
        'assignment_stats': assignment_stats,
        'recent_assignments': recent_assignments,
        'recent_students': recent_students,
        'recent_activity': recent_activity,
        'submission_rate': round(submission_rate, 1),
        'average_rating': 4.8,
        'completion_rate': 65,  # This would be calculated
        'satisfaction_percentage': 92,  # This would be calculated
        'response_time': '2.1h',
        'response_time_percentage': 85,
    }
    
    return render(request, 'courses/instructor_dashboard.html', context)

@login_required
def create_course(request):
    if not hasattr(request.user, 'instructor'):
        messages.error(request, 'You need to be an instructor to create courses.')
        return redirect('pages:home')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user.instructor
            
            save_draft = request.POST.get('save_draft')
            if save_draft:
                course.is_published = False
                message = 'Course saved as draft successfully!'
            else:
                course.is_published = True
                message = 'Course created and published successfully!'
            
            course.save()
            messages.success(request, message)
            return redirect('courses:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    
    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def edit_course(request, pk):
    if not hasattr(request.user, 'instructor'):
        messages.error(request, 'You need to be an instructor to edit courses.')
        return redirect('courses:home')
    
    course = get_object_or_404(Course, pk=pk, instructor=request.user.instructor)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:instructor_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/course_form.html', {'form': form})


# Lesson Management Views
@login_required
def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    
    # Convert markdown to HTML with proper code block handling
    if lesson.content:
        lesson.content_html = mark_safe(markdown.markdown(
            lesson.content,
            extensions=[
                'fenced_code',  # For code blocks with ```
                'codehilite',   # For syntax highlighting
                'tables',       # For tables
                'nl2br',        # For line breaks
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                    'guess_lang': True,
                }
            }
        ))
    else:
        lesson.content_html = ""
    
    user_lessons_progress = LessonProgress.objects.filter(
        user=request.user,
        lesson__course=course,
        completed=True
    )
    
    completed_lesson_ids = user_lessons_progress.values_list('lesson_id', flat=True)
    completed_lessons_count = user_lessons_progress.count()
    total_lessons = course.lessons.count()
    
    progress_percentage = 0
    if total_lessons > 0:
        progress_percentage = int((completed_lessons_count / total_lessons) * 100)
    
    lesson_completed = lesson.pk in completed_lesson_ids
    
    course_completed = Enrollment.objects.filter(
        user=request.user,
        course=course,
        completed=True
    ).exists()
    
    lessons = course.lessons.all().order_by('order')
    lesson_list = list(lessons)
    
    current_index = None
    for index, l in enumerate(lesson_list):
        if l.pk == lesson.pk:
            current_index = index
            break
    
    previous_lesson = None
    next_lesson = None
    
    if current_index is not None:
        if current_index > 0:
            previous_lesson = lesson_list[current_index - 1]
        if current_index < len(lesson_list) - 1:
            next_lesson = lesson_list[current_index + 1]
    
    context = {
        'course': course,
        'lesson': lesson,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'progress_percentage': progress_percentage,
        'completed_lessons': completed_lessons_count,
        'total_lessons': total_lessons,
        'completed_lesson_ids': list(completed_lesson_ids),
        'lesson_completed': lesson_completed,
        'course_completed': course_completed,
    }
    
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def create_lesson(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user.instructor)
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('courses:manage_lessons', course_pk=course_pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        last_lesson = course.lessons.order_by('-order').first()
        initial_order = last_lesson.order + 1 if last_lesson else 1
        
        form = LessonForm(initial={
            'order': initial_order,
            'content': '# Learning Objectives\n\n* Objective 1\n* Objective 2\n* Objective 3\n\n## Introduction\n\nStart your lesson content here...\n\n## Key Concepts\n\n* Point 1\n* Point 2\n* Point 3\n\n## Summary\n\nWrap up your lesson with key takeaways...'
        })
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/lesson_form.html', context)


@login_required
def edit_lesson(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user.instructor)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, course=course)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')
            return redirect('courses:manage_lessons', course_pk=course_pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LessonForm(instance=lesson)
    
    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'courses/lesson_form.html', context)


@login_required
def manage_lessons(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user.instructor)
    lessons = course.lessons.all().order_by('order')
    
    total_duration = lessons.aggregate(total_duration=Sum('duration_minutes'))['total_duration'] or 0
    videos_count = lessons.filter(video_url__isnull=False).count()
    
    context = {
        'course': course,
        'lessons': lessons,
        'total_duration': total_duration,
        'videos_count': videos_count,
    }
    return render(request, 'courses/manage_lessons.html', context)


@login_required
def create_lesson_quick(request):
    if request.method == 'POST':
        course_pk = request.POST.get('course')
        title = request.POST.get('title')
        order = request.POST.get('order', 0)
        
        course = get_object_or_404(Course, pk=course_pk, instructor=request.user.instructor)
        
        lesson = Lesson.objects.create(
            course=course,
            title=title,
            order=order,
            content="Add your lesson content here...",
        )
        messages.success(request, f'Lesson "{title}" created successfully!')
        return redirect('courses:instructor_dashboard')
    
    return redirect('courses:create_lesson')


@login_required
def update_lesson_order(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            for lesson_data in data['lessons']:
                lesson = Lesson.objects.get(
                    id=lesson_data['id'],
                    course__instructor=request.user.instructor
                )
                lesson.order = lesson_data['order']
                lesson.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})


@login_required
def delete_lesson(request, course_pk, lesson_pk):
    lesson = get_object_or_404(
        Lesson, 
        pk=lesson_pk, 
        course__pk=course_pk,
        course__instructor=request.user.instructor
    )
    if request.method == 'POST':
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f'Lesson "{lesson_title}" deleted successfully!')
        return redirect('courses:manage_lessons', course_pk=course_pk)
    return redirect('courses:manage_lessons', course_pk=course_pk)


# Miscellaneous Views
def get_certify(request):
    return redirect('courses:course_list')


# Assignment Views with Multiple Questions
@login_required
def assignment_list(request, course_pk):
    """List all assignments for a course"""
    course = get_object_or_404(Course, pk=course_pk)
    assignments = course.assignments.filter(is_published=True).order_by('order')
    
    # Check user submissions
    for assignment in assignments:
        submission = AssignmentSubmission.objects.filter(
            assignment=assignment, 
            user=request.user
        ).first()
        assignment.user_submission = submission
        assignment.question_count = assignment.get_question_count()
        assignment.total_points = assignment.get_total_points()
    
    context = {
        'course': course,
        'assignments': assignments,
    }
    return render(request, 'courses/assignment_list.html', context)


@login_required
def assignment_detail(request, course_pk, assignment_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    if request.user.is_staff:
        assignment = get_object_or_404(Assignment, pk=assignment_pk, course=course)
    else:
        assignment = get_object_or_404(Assignment, pk=assignment_pk, course=course, is_published=True)
    
    submission = AssignmentSubmission.objects.filter(
        assignment=assignment, user=request.user
    ).first()

    mc_questions = assignment.multiplechoicequestion_questions.all()
    code_questions = assignment.codequestion_questions.all()
    text_questions = assignment.textquestion_questions.all()

    if request.method == 'POST' and not submission:
        return handle_assignment_submission(request, course_pk, assignment_pk, assignment)
    
    context = {
        'course': course,
        'assignment': assignment,
        'submission': submission,
        'mc_questions': mc_questions,
        'code_questions': code_questions,
        'text_questions': text_questions,
        'total_points': assignment.get_total_points(),
        'question_count': assignment.get_question_count(),
    }
    
    return render(request, 'courses/assignment_detail.html', context)



def handle_assignment_submission(request, course_pk, assignment_pk, assignment):
    """Handle submission of assignment with multiple questions"""
    # Create assignment submission
    submission = AssignmentSubmission.objects.create(
        assignment=assignment,
        user=request.user
    )
    
    total_score = 0
    
    # Handle multiple choice submissions
    for question in assignment.multiplechoicequestion_set.all():
        selected_answer = request.POST.get(f'mc_{question.id}')
        if selected_answer:
            is_correct = selected_answer == question.correct_answer
            score = question.points if is_correct else 0
            
            MultipleChoiceSubmission.objects.create(
                submission=submission,
                question=question,
                selected_answer=selected_answer,
                score=score,
                is_correct=is_correct,
                feedback=question.explanation if is_correct else "Incorrect answer"
            )
            total_score += score
    
    # Handle code submissions
    for question in assignment.codequestion_set.all():
        code = request.POST.get(f'code_{question.id}')
        language = request.POST.get(f'language_{question.id}', question.language)
        
        if code:
            # Execute code and evaluate
            executor = CodeExecutor(timeout=question.timeout_seconds)
            execution_result = executor.evaluate_code(
                code,
                language,
                question.test_cases
            )
            
            # Calculate score
            passed_tests = [r for r in execution_result.get('results', []) if r.get('passed')]
            score = (len(passed_tests) / len(question.test_cases)) * question.points if question.test_cases else 0
            is_correct = len(passed_tests) == len(question.test_cases)
            
            CodeSubmission.objects.create(
                submission=submission,
                question=question,
                code=code,
                language=language,
                execution_result=execution_result,
                score=score,
                is_correct=is_correct,
                feedback=json.dumps(execution_result)
            )
            total_score += score
    
    # Handle text submissions
    for question in assignment.textquestion_set.all():
        answer_text = request.POST.get(f'text_{question.id}')
        
        if answer_text:
            # Simple keyword matching for auto-grading
            expected_answer = question.expected_answer.lower()
            user_answer = answer_text.lower()
            
            expected_keywords = set(expected_answer.split())
            user_keywords = set(user_answer.split())
            matching_keywords = expected_keywords.intersection(user_keywords)
            
            similarity = len(matching_keywords) / len(expected_keywords) if expected_keywords else 0
            score = similarity * question.points
            is_correct = similarity > 0.8
            
            TextSubmission.objects.create(
                submission=submission,
                question=question,
                answer_text=answer_text,
                score=score,
                is_correct=is_correct,
                feedback=f"Answer similarity: {similarity:.2%}"
            )
            total_score += score
    
    # Update total score
    submission.total_score = total_score
    submission.is_completed = True
    submission.save()
    
    messages.success(request, f'Assignment submitted! Total score: {total_score:.1f}/{assignment.get_total_points()}')
    return redirect('courses:assignment_detail', course_pk=course_pk, assignment_pk=assignment_pk)


# Instructor views for managing assignments
@login_required
def manage_assignments(request, course_pk):
    """Instructor view to manage assignments"""
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user.instructor)
    assignments = course.assignments.all().order_by('order')
    
    # Add question counts and total points
    for assignment in assignments:
        assignment.question_count = assignment.get_question_count()
        assignment.total_points = assignment.get_total_points()
    
    context = {
        'course': course,
        'assignments': assignments,
    }
    return render(request, 'courses/manage_assignments.html', context)


@login_required
def create_assignment(request, course_pk):
    """Create a new assignment with multiple questions"""
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user.instructor)
    
    if request.method == 'POST':
        assignment_form = AssignmentForm(request.POST)
        
        if assignment_form.is_valid():
            assignment = assignment_form.save(commit=False)
            assignment.course = course
            
            # Set order
            last_assignment = Assignment.objects.filter(course=course).order_by('-order').first()
            assignment.order = last_assignment.order + 1 if last_assignment else 1
            
            assignment.save()
            messages.success(request, 'Assignment created successfully! You can now add questions.')
            return redirect('courses:manage_assignment_questions', assignment_pk=assignment.pk)
    else:
        assignment_form = AssignmentForm()
    
    context = {
        'course': course,
        'form': assignment_form,
    }
    return render(request, 'courses/create_assignment.html', context)


@login_required
def manage_assignment_questions(request, assignment_pk):
    """Manage questions for an assignment"""
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructor=request.user.instructor)
    
    mc_questions = assignment.multiplechoicequestion_questions.all()
    code_questions = assignment.codequestion_questions.all()
    text_questions = assignment.textquestion_questions.all()
   
    context = {
        'assignment': assignment,
        'mc_questions': mc_questions,
        'code_questions': code_questions,
        'text_questions': text_questions,
        'total_points': assignment.get_total_points(),
        'question_count': assignment.get_question_count(),
    }
    return render(request, 'courses/manage_assignment_questions.html', context)


@login_required
def add_multiple_choice_question(request, assignment_pk):
    """Add multiple choice question to assignment"""
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructor=request.user.instructor)
    
    if request.method == 'POST':
        form = MultipleChoiceQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            
            # Set order
            last_question = MultipleChoiceQuestion.objects.filter(assignment=assignment).order_by('-order').first()
            question.order = last_question.order + 1 if last_question else 1
            
            question.save()
            messages.success(request, 'Multiple choice question added successfully!')
            return redirect('courses:manage_assignment_questions', assignment_pk=assignment.pk)
    else:
        form = MultipleChoiceQuestionForm()
    
    context = {
        'assignment': assignment,
        'form': form,
        'question_type': 'Multiple Choice',
    }
    return render(request, 'courses/add_question.html', context)


@login_required
def add_code_question(request, assignment_pk):
    """Add code question to assignment"""
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructor=request.user.instructor)
    
    if request.method == 'POST':
        form = CodeQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            
            # Parse test cases
            test_cases_json = request.POST.get('test_cases_json', '[]')
            try:
                question.test_cases = json.loads(test_cases_json)
            except json.JSONDecodeError:
                messages.error(request, 'Invalid test cases format. Please use valid JSON.')
                return render(request, 'courses/add_code_question.html', {'assignment': assignment, 'form': form})
            
            # Set order
            last_question = CodeQuestion.objects.filter(assignment=assignment).order_by('-order').first()
            question.order = last_question.order + 1 if last_question else 1
            
            question.save()
            messages.success(request, 'Code question added successfully!')
            return redirect('courses:manage_assignment_questions', assignment_pk=assignment.pk)
    else:
        form = CodeQuestionForm()
    
    context = {
        'assignment': assignment,
        'form': form,
        'question_type': 'Code',
    }
    return render(request, 'courses/add_code_question.html', context)


@login_required
def add_text_question(request, assignment_pk):
    """Add text question to assignment"""
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructor=request.user.instructor)
    
    if request.method == 'POST':
        form = TextQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            
            # Set order
            last_question = TextQuestion.objects.filter(assignment=assignment).order_by('-order').first()
            question.order = last_question.order + 1 if last_question else 1
            
            question.save()
            messages.success(request, 'Text question added successfully!')
            return redirect('courses:manage_assignment_questions', assignment_pk=assignment.pk)
    else:
        form = TextQuestionForm()
    
    context = {
        'assignment': assignment,
        'form': form,
        'question_type': 'Text',
    }
    return render(request, 'courses/add_text_question.html', context)


@login_required
def view_submissions(request, assignment_pk):
    """Instructor view to see all submissions for an assignment"""
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__instructor=request.user.instructor)
    submissions = assignment.submissions.all().select_related('user').order_by('-submitted_at')
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
        'course': assignment.course,
    }
    return render(request, 'courses/assignment_submissions.html', context)

def delete_course(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user)
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect('instructor_dashboard')


def add_multiple_choice_question(request, course_pk, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course__pk=course_pk)
    form = MultipleChoiceQuestionForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.save()

            # Count how many questions are done
            total_added = assignment.multiplechoicequestion_set.count()
            total_required = assignment.total_questions

            if total_added < total_required:
                messages.success(
                    request,
                    f"Question {total_added} added! Please add question {total_added + 1} of {total_required}."
                )
                return redirect('add_multiple_choice_question', course_pk=course_pk, assignment_pk=assignment_pk)
            else:
                messages.success(
                    request,
                    f"All {total_required} questions have been added successfully!"
                )
                return redirect('assignment_detail', course_pk=course_pk, assignment_pk=assignment_pk)
    else:
        total_added = assignment.multiplechoicequestion_set.count()
        total_required = assignment.total_questions

        if total_added >= total_required:
            messages.info(request, "All questions for this assignment are already added.")
            return redirect('assignment_detail', course_pk=course_pk, assignment_pk=assignment_pk)

    context = {
        'form': form,
        'assignment': assignment,
    }
    return render(request, 'courses/add_assignment.html', context)




def add_question(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    form = MultipleChoiceQuestionForm(request.POST or None)

    # Count how many questions are already added
    current_count = assignment.multiplechoicequestion_questions.count()

    if request.method == "POST":
        if current_count >= assignment.total_questions:
            messages.warning(request, f"You’ve already added all {assignment.total_questions} questions.")
            return redirect('courses:manage_assignment_questions', assignment_id=assignment.id)

        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.order = current_count + 1
            question.save()

            current_count += 1
            remaining = assignment.total_questions - current_count

            if remaining > 0:
                messages.success(request, f"Question added successfully! You can add {remaining} more question{'s' if remaining != 1 else ''}.")
                return redirect('courses:add_question', assignment_id=assignment.id)
            else:
                messages.success(request, f"All {assignment.total_questions} questions added successfully!")
                return redirect('courses:manage_assignment_questions', assignment_id=assignment.id)
    else:
        if current_count >= assignment.total_questions:
            messages.info(request, f"All {assignment.total_questions} questions are already added.")
            return redirect('courses:manage_assignment_questions', assignment_id=assignment.id)

    context = {
        'assignment': assignment,
        'form': form,
        'current_count': current_count,
        'remaining': assignment.total_questions - current_count,
    }
    return render(request, 'courses/add_question.html', context)


@login_required
def edit_assignment(request, course_pk, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course_id=course_pk)
    if request.user != assignment.created_by and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to edit this assignment.")
    
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('courses:assignment_detail', course_pk=course_pk, assignment_pk=assignment_pk)
    else:
        form = AssignmentForm(instance=assignment)

    return render(request, 'courses/edit_assignment.html', {'form': form, 'assignment': assignment})


@login_required
def delete_assignment(request, course_pk, assignment_pk):
    assignment = get_object_or_404(Assignment, pk=assignment_pk, course_id=course_pk)
    if request.user != assignment.created_by and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to delete this assignment.")

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('courses:assignment_list', course_pk=course_pk)

    return render(request, 'courses/delete_assignment_confirm.html', {'assignment': assignment})
