from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from courses.models import Enrollment
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from courses.models import Course, Enrollment, Certificate, ExamSubmission,Notification,AssignmentSubmission
from django.db.models import Avg, Count,Q
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.urls import reverse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Avg, Case, When, IntegerField, Sum
from courses.models import Course, Certificate, Enrollment, ExamSubmission
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from courses.models import Course, Lesson, Assignment, Exam
from courses.forms import CourseForm, LessonForm, AssignmentForm, ExamForm
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from courses.models import Course   # adjust if your model is named differently
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Career, BlogPost, BlogCategory, BlogComment
from django.contrib import messages

@login_required
def submit_review(request, course_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        # Save review logic here
        return redirect('courses:course_detail', course_id=course_id)

def security_settings(request):
    return render(request, "accounts/security_settings.html")

def mfa_setup(request):
    return render(request, "accounts/mfa_setup.html")
def mfa_verify(request):
    # verify the OTP here
    return render(request, "accounts/mfa_verify.html")
# ---------- CAREERS ----------
def career_list(request, page=1):
    jobs = Career.objects.filter(is_active=True).order_by("-created_at")
    paginator = Paginator(jobs, 5)  # 5 jobs per page
    page_obj = paginator.get_page(page)

    return render(request, "accounts/career_list.html", {
        "page_obj": page_obj,
    })

from .models import BlogPost  # adjust to your model
from .models import Subscriber  # optional, if you want to save subscribers

def subscribe(request):
    """
    Handle newsletter/email subscription.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            # Save subscriber if you have a model
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "Thank you for subscribing!")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, "Please provide a valid email.")
    return render(request, 'accounts/subscribe.html')
def newsletter_subscribe(request):
    """
    Handle newsletter subscription form submission.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "Thank you for subscribing!")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, "Please provide a valid email.")
    return render(request, 'accounts/newsletter_subscribe.html')
from .models import BlogCategory, BlogPost

def blog_category(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(category=category, published=True)
    return render(request, 'accounts/blog_category.html', {'category': category, 'posts': posts})
def contribute(request):
    """
    Page where users can contribute content, feedback, or resources.
    """
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if name and email and message:
            # Save to database or send email
            messages.success(request, "Thank you for your contribution!")
        else:
            messages.error(request, "All fields are required.")
    
    return render(request, 'accounts/contribute.html')
def blog_search(request):
    """
    Search blog posts by keyword.
    """
    query = request.GET.get('q', '')
    results = BlogPost.objects.filter(title__icontains=query) if query else []
    return render(request, 'accounts/blog_search.html', {'query': query, 'results': results})
def career_detail(request, slug):
    job = get_object_or_404(Career, slug=slug)
    return render(request, "accounts/career_detail.html", {"job": job})


# ---------- BLOG ----------
def blog_list(request, page=1):
    posts = BlogPost.objects.filter(published=True).order_by("-created_at")
    categories = BlogCategory.objects.all()

    paginator = Paginator(posts, 5)
    page_obj = paginator.get_page(page)

    return render(request, "accounts/blog_list.html", {
        "page_obj": page_obj,
        "categories": categories,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = BlogComment.objects.filter(post=post).order_by("-created_at")
    categories = BlogCategory.objects.all()

    return render(request, "accounts/blog_detail.html", {
        "post": post,
        "comments": comments,
        "categories": categories,
    })


# ---------- ADD COMMENT ----------
def add_comment(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)

    if request.method == "POST":
        name = request.POST.get("name")
        comment = request.POST.get("comment")

        if not name or not comment:
            messages.error(request, "All fields are required.")
            return redirect("accounts:blog_detail", slug=slug)

        BlogComment.objects.create(
            post=post, name=name, comment=comment
        )
        messages.success(request, "Comment added successfully.")
        return redirect("accounts:blog_detail", slug=slug)

def home(request):
    return render(request,'home.html')
@login_required
@require_POST
def course_bulk_action(request):
    """
    Handle bulk actions on selected courses.
    Supported actions: delete, activate, deactivate
    """

    action = request.POST.get("action")
    course_ids = request.POST.getlist("course_ids")

    if not course_ids:
        messages.error(request, "No courses selected.")
        return redirect("courses:course_list")

    courses = Course.objects.filter(id__in=course_ids)

    if action == "delete":
        count = courses.count()
        courses.delete()
        messages.success(request, f"{count} courses deleted successfully.")

    elif action == "activate":
        count = courses.update(is_active=True)
        messages.success(request, f"{count} courses activated.")

    elif action == "deactivate":
        count = courses.update(is_active=False)
        messages.success(request, f"{count} courses deactivated.")

    else:
        messages.error(request, "Invalid action selected.")

    return redirect("courses:course_list")

# ----------------------------
# Course CRUD
# ----------------------------
@staff_member_required
def admin_course_detail(request):
    courses = Course.objects.all()
    return render(request, "courses/course_list.html", {"courses": courses})


@staff_member_required
def admin_course_add(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully.")
            return redirect("accounts:course_detail")
    else:
        form = CourseForm()
    return render(request, "admin/course_form.html", {"form": form, "title": "Add Course"})

@staff_member_required
def admin_course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect("accounts:course_list")
    else:
        form = CourseForm(instance=course)
    return render(request, "admin/course_form.html", {"form": form, "title": "Edit Course"})

@staff_member_required
def admin_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect("accounts:course_list")


# ----------------------------
# Lesson CRUD
# ----------------------------
@staff_member_required
def admin_lesson_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    return render(request, "admin/lesson_list.html", {"course": course, "lessons": lessons})

@staff_member_required
def admin_lesson_add(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Lesson added successfully.")
            return redirect("accounts:lesson_list", course_id=course.id)
    else:
        form = LessonForm()
    return render(request, "admin/lesson_form.html", {"form": form, "course": course, "title": "Add Lesson"})

@staff_member_required
def admin_lesson_edit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully.")
            return redirect("accounts:lesson_list", course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, "admin/lesson_form.html", {"form": form, "course": lesson.course, "title": "Edit Lesson"})

@staff_member_required
def admin_lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.course.id
    lesson.delete()
    messages.success(request, "Lesson deleted successfully.")
    return redirect("accounts:lesson_list", course_id=course_id)


# ----------------------------
# Assignment CRUD
# ----------------------------
@staff_member_required
def admin_assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = course.assignments.all()
    return render(request, "admin/assignment_list.html", {"course": course, "assignments": assignments})

@staff_member_required
def admin_assignment_add(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, "Assignment added successfully.")
            return redirect("accounts:assignment_list", course_id=course.id)
    else:
        form = AssignmentForm()
    return render(request, "admin/assignment_form.html", {"form": form, "course": course, "title": "Add Assignment"})

@staff_member_required
def admin_assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully.")
            return redirect("accounts:assignment_list", course_id=assignment.course.id)
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, "admin/assignment_form.html", {"form": form, "course": assignment.course, "title": "Edit Assignment"})

@staff_member_required
def admin_assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course_id = assignment.course.id
    assignment.delete()
    messages.success(request, "Assignment deleted successfully.")
    return redirect("accounts:assignment_list", course_id=course_id)


# ----------------------------
# Exam CRUD
# ----------------------------
@staff_member_required
def admin_exam_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    exams = course.exams.all()
    return render(request, "admin/exam_list.html", {"course": course, "exams": exams})

@staff_member_required
def admin_exam_add(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.course = course
            exam.save()
            messages.success(request, "Exam added successfully.")
            return redirect("accounts:exam_list", course_id=course.id)
    else:
        form = ExamForm()
    return render(request, "admin/exam_form.html", {"form": form, "course": course, "title": "Add Exam"})

@staff_member_required
def admin_exam_edit(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam updated successfully.")
            return redirect("accounts:exam_list", course_id=exam.course.id)
    else:
        form = ExamForm(instance=exam)
    return render(request, "admin/exam_form.html", {"form": form, "course": exam.course, "title": "Edit Exam"})

@staff_member_required
def admin_exam_delete(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    course_id = exam.course.id
    exam.delete()
    messages.success(request, "Exam deleted successfully.")
    return redirect("accounts:exam_list", course_id=course_id)



@staff_member_required
def admin_dashboard(request):
    # -----------------------------
    # Basic stats
    # -----------------------------
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_certificates = Certificate.objects.count()
    total_lessons = Lesson.objects.count()
    total_assignments = Assignment.objects.count()
    total_exams = Exam.objects.count()
    
    # Additional detailed stats - USING CORRECT FIELD NAMES
    active_users = User.objects.filter(is_active=True).count()
    active_courses = Course.objects.filter(published=True).count()  # Changed from is_active to published
    published_lessons = Lesson.objects.filter(is_published=True).count()
    # published_lessons = Lesson.objects.count()
    upcoming_exams = Exam.objects.filter(scheduled_date__gt=timezone.now()).count()
    
    # Today's metrics
    today = timezone.now().date()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    # new_certificates_today = Certificate.objects.filter(issued_date__date=today).count()
    new_certificates_today = Certificate.objects.filter(issued_at__date=today).count()

    
    # User distribution
    student_count = User.objects.filter(is_staff=False, is_superuser=False).count()
    instructor_count = User.objects.filter(groups__name='Instructor').count()
    staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
    admin_count = User.objects.filter(is_superuser=True).count()
    
    # Enrollment and completion stats
    total_enrollments = Enrollment.objects.count()
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5]
    
    # Performance metrics (these would be calculated from your actual data)
    completion_rate = 75
    avg_exam_score = 82.5
    pass_rate = 78
    avg_course_completion = 65
    assignment_completion_rate = 72
    engagement_rate = 68
    
    # System metrics
    active_sessions = 142
    response_time = 124
    error_rate = 0.2
    requests_per_minute = 245
    
    # Pending submissions
    pending_submissions = 23
    
    # Draft courses count
    draft_courses = Course.objects.filter(published=False).count()  # Added this for draft count
    
    # Exam stats
    total_submissions = ExamSubmission.objects.count()
    passed_count = ExamSubmission.objects.filter(passed=True).count()
    failed_count = ExamSubmission.objects.filter(passed=False).count()
    
    exam_stats = {
        'total_submissions': total_submissions,
        'passed_count': passed_count,
        'failed_count': failed_count,
    }

    # Charts data
    certs_per_course = Certificate.objects.values('course__title').annotate(total=Count('id'))
    certs_labels = [c['course__title'] for c in certs_per_course]
    certs_data = [c['total'] for c in certs_per_course]

    exams = ExamSubmission.objects.values('exam__title').distinct()
    exam_labels = []
    passed_data = []
    failed_data = []

    for e in exams:
        exam_title = e['exam__title']
        exam_labels.append(exam_title)
        passed = ExamSubmission.objects.filter(exam__title=exam_title, passed=True).count()
        failed = ExamSubmission.objects.filter(exam__title=exam_title, passed=False).count()
        passed_data.append(passed)
        failed_data.append(failed)

    # Recent Activity
    recent_activity = [
        {
            'user': request.user,
            'action': 'Created',
            'action_color': 'success',
            'action_icon': 'plus-circle',
            'details': 'New course "Advanced Python Programming"',
            'timestamp': timezone.now() - timezone.timedelta(minutes=45),
            'status_color': 'success'
        },
        {
            'user': request.user,
            'action': 'Updated',
            'action_color': 'warning',
            'action_icon': 'pencil',
            'details': 'User permissions for john_doe',
            'timestamp': timezone.now() - timezone.timedelta(hours=2),
            'status_color': 'success'
        },
        {
            'user': request.user,
            'action': 'Published',
            'action_color': 'info',
            'action_icon': 'globe',
            'details': 'Lesson "Database Design Patterns"',
            'timestamp': timezone.now() - timezone.timedelta(hours=5),
            'status_color': 'success'
        },
        {
            'user': request.user,
            'action': 'Deleted',
            'action_color': 'danger',
            'action_icon': 'trash',
            'details': 'Old assignment "Introduction Quiz"',
            'timestamp': timezone.now() - timezone.timedelta(days=1),
            'status_color': 'success'
        },
    ]

    # System alerts
    system_alerts = [
        {
            'type': 'warning',
            'icon': 'exclamation-triangle',
            'title': 'Storage Warning',
            'message': 'Disk usage at 85%'
        },
        {
            'type': 'info',
            'icon': 'info-circle',
            'title': 'Maintenance',
            'message': 'Scheduled maintenance tonight at 2 AM'
        }
    ]

    context = {
        # Basic counts
        "total_users": total_users,
        "total_courses": total_courses,
        "total_certificates": total_certificates,
        "total_lessons": total_lessons,
        "total_assignments": total_assignments,
        "total_exams": total_exams,
        
        # Detailed metrics - USING CORRECT FIELD NAMES
        "active_users": active_users,
        "active_courses": active_courses,  # Now using published=True
        "published_lessons": published_lessons,
        "upcoming_exams": upcoming_exams,
        "new_users_today": new_users_today,
        "new_certificates_today": new_certificates_today,
        "total_enrollments": total_enrollments,
        "pending_submissions": pending_submissions,
        "draft_courses": draft_courses,  # Added for template consistency
        
        # User distribution
        "student_count": student_count,
        "instructor_count": instructor_count,
        "staff_count": staff_count,
        "admin_count": admin_count,
        
        # Performance metrics
        "completion_rate": completion_rate,
        "avg_exam_score": avg_exam_score,
        "pass_rate": pass_rate,
        "avg_course_completion": avg_course_completion,
        "assignment_completion_rate": assignment_completion_rate,
        "engagement_rate": engagement_rate,
        
        # System metrics
        "active_sessions": active_sessions,
        "response_time": response_time,
        "error_rate": error_rate,
        "requests_per_minute": requests_per_minute,
        
        # Charts data
        "recent_enrollments": recent_enrollments,
        "exam_stats": exam_stats,
        "certs_labels": json.dumps(certs_labels),
        "certs_data": json.dumps(certs_data),
        "exam_labels": json.dumps(exam_labels),
        "passed_data": json.dumps(passed_data),
        "failed_data": json.dumps(failed_data),
        "recent_activity": recent_activity,
        "system_alerts": system_alerts,
    }

    return render(request, "accounts/admin_dashboard.html", context)
def verify_email(request, token):
    try:
        profile = Profile.objects.get(email_verification_token=token)
        user = profile.user
        user.is_active = True
        user.save()

        profile.email_verification_token = ""
        profile.save()

        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect("accounts:login")

    except Profile.DoesNotExist:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("accounts:login")

def register(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not password1 or not password2:
            messages.error(request, "Please enter both password fields.")
            return render(request, "accounts/register.html", {"next": next_url})

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html", {"next": next_url})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                is_active=False
            )

            profile, created = Profile.objects.get_or_create(user=user)

            token = get_random_string(32)
            profile.email_verification_token = token
            profile.save()

            verification_link = request.build_absolute_uri(
                reverse("accounts:verify_email", args=[token])
            )

            subject = "Verify your Codelab account"
            body = f"Hi {user.username},\n\nPlease verify your account using this link:\n{verification_link}\n\nThank you!"
            EmailMessage(subject, body, to=[email]).send()

            messages.success(
                request,
                "Account created! Please check your email to verify your account."
            )

            return redirect(next_url or "accounts:login")

    return render(request, "accounts/register.html", {"next": next_url})





from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')  # Already logged in

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Optional checkbox

        # Authenticate user by username
        user = authenticate(request, username=username_or_email, password=password)

        # Try email authentication if username failed
        if not user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            
            # Session expiry: remember me
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Expires on browser close

            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")

            # Redirect to 'next' parameter if safe
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username/email or password. Please try again.")

    # GET request
    return render(request, 'accounts/login.html', {
        'next': request.GET.get('next', '')
    })





    
# ----------------------------
# Login redirect: check profile
# ----------------------------
@login_required
def login_redirect(request):
    """
    Redirects users after login based on their role:
    - Superuser / Staff → admin_dashboard
    - Student → dashboard
    """
    user = request.user

    # Superuser / Staff → admin dashboard
    if user.is_superuser or user.is_staff:
        return redirect("accounts:admin_dashboard")

    # Ensure Profile exists
    profile, created = Profile.objects.get_or_create(user=user)

    # If profile not updated, redirect to update_profile first
    if not profile.updated:
        return redirect("accounts:update_profile")

    # Normal student → student dashboard
    return redirect("accounts:dashboard")



# ----------------------------
# Update Profile
@login_required
def update_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # <--- add request.FILES
        if form.is_valid():
            profile = form.save(commit=False)
            profile.updated = True
            profile.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("accounts:dashboard")
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, "accounts/update_profile.html", {"form": form})


# ----------------------------
# Logout
# ----------------------------
def logout_view(request):
    logout(request)
    return redirect("accounts:home")

@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    courses_progress = []
    upcoming_items = []  # unified exams & assignments

    for e in enrollments:
        course = e.course
        # -----------------------------
        # Progress
        # -----------------------------
        total_lessons = course.lessons.count()
        completed_lessons = e.completed_lessons.count() if hasattr(e, 'completed_lessons') else 0
        progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        courses_progress.append({"course": course, "progress": progress})

        # -----------------------------
        # Upcoming Exams
        # -----------------------------
        for exam in course.exams.filter(scheduled_date__gte=timezone.now()):
            if not ExamSubmission.objects.filter(exam=exam, student=request.user).exists():
                upcoming_items.append({
                    "type": "Exam",
                    "title": exam.title,
                    "course": course,
                    "due_date": exam.scheduled_date,
                    "link": exam.get_absolute_url() if hasattr(exam, 'get_absolute_url') else None
                })
                # Create notification if missing
                if not Notification.objects.filter(user=request.user, message__icontains=exam.title).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=f"Upcoming Exam: {exam.title} for course {course.title} on {exam.scheduled_date.strftime('%d %b %Y')}",
                        link=exam.get_absolute_url() if hasattr(exam, 'get_absolute_url') else None
                    )

        # -----------------------------
        # Upcoming Assignments
        # -----------------------------
        for assignment in course.assignments.filter(due_date__gte=timezone.now()):
            if not AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).exists():
                upcoming_items.append({
                    "type": "Assignment",
                    "title": assignment.title,
                    "course": course,
                    "due_date": assignment.due_date,
                    "link": None  # optional: add assignment detail page URL
                })
                if not Notification.objects.filter(user=request.user, message__icontains=assignment.title).exists():
                    Notification.objects.create(
                        user=request.user,
                        message=f"Upcoming Assignment: {assignment.title} for course {course.title} due on {assignment.due_date.strftime('%d %b %Y')}",
                    )

    # -----------------------------
    # Certificates
    # -----------------------------
    certificates = Certificate.objects.filter(user=request.user)

    # -----------------------------
    # Notifications
    # -----------------------------
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    # -----------------------------
    # Data for Chart.js
    # -----------------------------
    progress_labels = [c['course'].title for c in courses_progress]
    progress_data = [c['progress'] for c in courses_progress]

    return render(request, "accounts/dashboard.html", {
        "courses_progress": courses_progress,
        "certificates": certificates,
        "upcoming_items": upcoming_items,
        "progress_labels": json.dumps(progress_labels),
        "progress_data": json.dumps(progress_data),
        "notifications": notifications,
    })

    # -----------------------------
    # Certificates
    # -----------------------------
    certificates = Certificate.objects.filter(user=request.user)

    # -----------------------------
    # Notifications
    # -----------------------------
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    # -----------------------------
    # JSON for Charts
    # -----------------------------
    progress_labels = [c['course'].title for c in courses_progress]
    progress_data = [c['progress'] for c in courses_progress]

    return render(request, "accounts/dashboard.html", {
        "courses_progress": courses_progress,
        "certificates": certificates,
        "upcoming_items": sorted(upcoming_items, key=lambda x: x['due_date']),  # sort by due date
        "progress_labels": json.dumps(progress_labels),
        "progress_data": json.dumps(progress_data),
        "notifications": notifications,
    })



from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({"status": "success"})
    except Notification.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Notification not found"}, status=404)

@login_required
def fetch_unread_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-created_at')[:10]
    
    data = [
        {
            "id": n.id,
            "message": n.message,
            "link": n.link or "#",
            "created_at": n.created_at.strftime("%d %b %Y %H:%M")
        } for n in notifications
    ]
    return JsonResponse({
        "notifications": data, 
        "count": notifications.count()
    })

@login_required
@require_http_methods(["POST", "GET"])
def mark_all_notifications_read(request):
    if request.method == "POST" or request.method == "GET":
        updated_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({"status": "success", "updated_count": updated_count})
        
        messages.success(request, f"Marked {updated_count} notifications as read.")
        return redirect(request.META.get('HTTP_REFERER', 'accounts:dashboard'))
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            # Generate a temporary token or new password
            temp_password = get_random_string(8)
            user.set_password(temp_password)
            user.save()

            # Send email with temp password
            send_mail(
                subject="Password Reset - Codelab",
                message=f"Your temporary password is: {temp_password}\nPlease login and change it immediately.",
                from_email="noreply@codelab.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, "A temporary password has been sent to your email.")
        except User.DoesNotExist:
            messages.error(request, "No user found with that email.")
        return redirect("accounts:login")
    
    return render(request, "accounts/forgot_password.html")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:update_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


# ----------------------------
# Static Pages
# ----------------------------

def about(request):
    return render(request, "pages/about.html")


def faq(request):
    return render(request, "pages/faq.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def terms(request):
    return render(request, "pages/terms.html")


def support(request):
    return render(request, "pages/support.html")


# ----------------------------
# Contact Form Page
# ----------------------------
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not name or not email or not message:
            messages.error(request, "All fields are required.")
            return redirect("accounts:contact")

        # Email sending (adjust settings properly)
        send_mail(
            subject=f"New Contact Message from {name}",
            message=f"Sender Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent. We'll respond shortly.")
        return redirect("accounts:contact")

    return render(request, "pages/contact.html")


# ----------------------------
# User Management
# ----------------------------
@staff_member_required
def admin_user_list(request):
    users = User.objects.all().select_related('profile')
    return render(request, "admin/user_list.html", {"users": users})

@staff_member_required
def admin_user_add(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        is_staff = request.POST.get("is_staff") == "on"
        is_active = request.POST.get("is_active") == "on"
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff,
                is_active=is_active
            )
            Profile.objects.create(user=user)
            messages.success(request, f"User {username} created successfully.")
            return redirect("accounts:admin_user_list")
    
    return render(request, "admin/user_form.html", {"title": "Add User"})

@staff_member_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.is_staff = request.POST.get("is_staff") == "on"
        user.is_active = request.POST.get("is_active") == "on"
        
        # Update password if provided
        new_password = request.POST.get("password")
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        # Update profile
        profile.full_name = request.POST.get("full_name")
        profile.phone = request.POST.get("phone")
        profile.save()
        
        messages.success(request, f"User {user.username} updated successfully.")
        return redirect("accounts:admin_user_list")
    
    return render(request, "admin/user_form.html", {
        "title": "Edit User",
        "user": user,
        "profile": profile
    })

@staff_member_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"User {username} deleted successfully.")
    return redirect("accounts:admin_user_list")

# ----------------------------
# Certificate Management
# ----------------------------
@staff_member_required
def admin_certificate_list(request):
    certificates = Certificate.objects.all().select_related('user', 'course')
    return render(request, "admin/certificate_list.html", {"certificates": certificates})

@staff_member_required
def admin_certificate_delete(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    certificate.delete()
    messages.success(request, "Certificate deleted successfully.")
    return redirect("accounts:admin_certificate_list")

# ----------------------------
# Global Content Management (All items)
# ----------------------------
@staff_member_required
def admin_lesson_list_all(request):
    lessons = Lesson.objects.all().select_related('course')
    return render(request, "admin/lesson_list_all.html", {"lessons": lessons})

# In your certificate list view
@staff_member_required
def admin_certificate_list(request):
    certificates = Certificate.objects.all().select_related('user', 'course')
    unique_students = certificates.values('user').distinct().count()
    unique_courses = certificates.values('course').distinct().count()
    this_month = certificates.filter(issued_date__month=timezone.now().month).count()
    
    return render(request, "admin/certificate_list.html", {
        "certificates": certificates,
        "unique_students": unique_students,
        "unique_courses": unique_courses,
        "this_month": this_month
    })

# In your global assignment list view
@staff_member_required
def admin_assignment_list_all(request):
    assignments = Assignment.objects.all().select_related('course')
    active_assignments = assignments.filter(is_active=True).count()
    overdue_assignments = assignments.filter(
        due_date__lt=timezone.now(), 
        is_active=True
    ).count()
    total_submissions = AssignmentSubmission.objects.count()
    
    return render(request, "admin/assignment_list_all.html", {
        "assignments": assignments,
        "active_assignments": active_assignments,
        "overdue_assignments": overdue_assignments,
        "total_submissions": total_submissions
    })

@staff_member_required
def admin_exam_list_all(request):
    exams = Exam.objects.all().select_related('course')

    # Precompute pass rates
    for exam in exams:
        total_submissions = exam.submissions.count()
        passed_submissions = exam.submissions.filter(passed=True).count()
        exam.pass_rate = int((passed_submissions / total_submissions) * 100) if total_submissions > 0 else 0

    active_exams = exams.filter(is_active=True).count()
    upcoming_exams = exams.filter(
        scheduled_date__gt=timezone.now()
    ).count()
    total_submissions = ExamSubmission.objects.count()

    return render(request, "admin/exam_list_all.html", {
        "exams": exams,
        "active_exams": active_exams,
        "upcoming_exams": upcoming_exams,
        "total_submissions": total_submissions
    })

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Exam, ExamQuestion, Course

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Exam, ExamQuestion, Course

@login_required
@permission_required('exams.add_exam', raise_exception=True)
def create_exam(request):
    courses = Course.objects.all()

    if request.method == 'POST':
        try:
            exam = Exam.objects.create(
                course_id=request.POST.get('course'),
                title=request.POST.get('title'),
                duration_minutes=request.POST.get('duration_minutes', 60),
                pass_mark=request.POST.get('pass_mark', 50),
                is_active='is_active' in request.POST,
                scheduled_date=request.POST.get('scheduled_date') or timezone.now()
            )

            # Create Questions
            question_indices = set()
            for key in request.POST:
                if key.startswith('questions['):
                    index = int(key.split('[')[1].split(']')[0])
                    question_indices.add(index)

            for index in sorted(question_indices):
                question_text = request.POST.get(f'questions[{index}][question_text]')
                if question_text:
                    ExamQuestion.objects.create(
                        exam=exam,
                        question_text=question_text,
                        choice_a=request.POST.get(f'questions[{index}][choice_a]'),
                        choice_b=request.POST.get(f'questions[{index}][choice_b]'),
                        choice_c=request.POST.get(f'questions[{index}][choice_c]'),
                        choice_d=request.POST.get(f'questions[{index}][choice_d]'),
                        correct_choice=request.POST.get(f'questions[{index}][correct_choice]'),
                        points=request.POST.get(f'questions[{index}][points]', 1)
                    )

            messages.success(request, f'Exam "{exam.title}" created successfully!')
            return redirect('accounts:exam_detail', exam_id=exam.id)

        except Exception as e:
            messages.error(request, f'Error creating exam: {str(e)}')

    return render(request, 'admin/exam_form.html', {
        'courses': courses,
        'questions': [],
        'selected_course': None,  # for template
    })


@login_required
@permission_required('exams.change_exam', raise_exception=True)
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    courses = Course.objects.all()
    questions = exam.questions.all()

    if request.method == 'POST':
        try:
            exam.course_id = request.POST.get('course')
            exam.title = request.POST.get('title')
            exam.duration_minutes = request.POST.get('duration_minutes', 60)
            exam.pass_mark = request.POST.get('pass_mark', 50)
            exam.is_active = 'is_active' in request.POST
            if request.POST.get('scheduled_date'):
                exam.scheduled_date = request.POST.get('scheduled_date')
            exam.save()

            # Delete existing questions and create new ones
            exam.questions.all().delete()

            question_indices = set()
            for key in request.POST:
                if key.startswith('questions['):
                    index = int(key.split('[')[1].split(']')[0])
                    question_indices.add(index)

            for index in sorted(question_indices):
                question_text = request.POST.get(f'questions[{index}][question_text]')
                if question_text:
                    ExamQuestion.objects.create(
                        exam=exam,
                        question_text=question_text,
                        choice_a=request.POST.get(f'questions[{index}][choice_a]'),
                        choice_b=request.POST.get(f'questions[{index}][choice_b]'),
                        choice_c=request.POST.get(f'questions[{index}][choice_c]'),
                        choice_d=request.POST.get(f'questions[{index}][choice_d]'),
                        correct_choice=request.POST.get(f'questions[{index}][correct_choice]'),
                        points=request.POST.get(f'questions[{index}][points]', 1)
                    )

            messages.success(request, f'Exam "{exam.title}" updated successfully!')
            return redirect('accounts:exam_detail', exam_id=exam.id)

        except Exception as e:
            messages.error(request, f'Error updating exam: {str(e)}')

    return render(request, 'admin/exam_form.html', {
        'form': exam,
        'courses': courses,
        'questions': questions,
        'selected_course': exam.course_id,  # <-- add this
    })

# ----------------------------
# Quick Add Views
# ----------------------------
@staff_member_required
def admin_lesson_add_quick(request):
    courses = Course.objects.all()
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson added successfully.")
            return redirect("accounts:admin_lesson_list_all")
    else:
        form = LessonForm()
    return render(request, "admin/quick_lesson_form.html", {
        "form": form, 
        "title": "Quick Add Lesson",
        "courses": courses
    })

@staff_member_required
def admin_assignment_add_quick(request):
    courses = Course.objects.all()

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        course_id = request.POST.get("course")   # Get course from select

        if not course_id:
            messages.error(request, "Please select a course.")
            return redirect("accounts:admin_assignment_add_quick")

        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = Course.objects.get(id=course_id)
            assignment.save()

            messages.success(request, "Assignment added successfully.")
            return redirect("accounts:admin_assignment_list_all")
    else:
        form = AssignmentForm()

    return render(request, "admin/quick_assignment_form.html", {
        "form": form,
        "title": "Quick Add Assignment",
        "courses": courses,
    })

@login_required
def profile_settings(request):
    return render(request, "accounts/profile_settings.html")

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from courses.models import Exam, Course
from courses.forms import ExamForm
@login_required
@permission_required('exams.add_exam', raise_exception=True)
def admin_exam_add_quick(request):
    """
    Quickly add an exam to a specific course.
    Handles GET (form display) and POST (form submission)
    """
    courses = Course.objects.all()
    course = None

    if request.method == "POST":
        course_id = request.POST.get("course_id")
        if not course_id:
            messages.error(request, "Please select a course.")
            return redirect("accounts:admin_exam_add_quick")

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            messages.error(request, "Selected course does not exist.")
            return redirect("accounts:admin_exam_add_quick")

        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.course = course  # assign course to avoid NOT NULL error
            exam.save()
            messages.success(request, "Exam created successfully!")
            return redirect("accounts:exam_list", course_id=course.id)
        else:
            messages.error(request, "There was an error creating the exam.")
    else:
        form = ExamForm()

    return render(request, "admin/admin_exam_add_quick.html", {
        "form": form,
        "courses": courses,
        "course": course,
    })

@staff_member_required
def admin_course_list(request):
    courses = Course.objects.all().prefetch_related('lessons', 'assignments', 'exams')
    
    # Apply filters - USING CORRECT FIELD NAMES
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'published':
        courses = courses.filter(published=True)  # Changed from is_published to published
    elif status_filter == 'draft':
        courses = courses.filter(published=False)  # Changed from is_published to published
    
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        courses = courses.filter(level=difficulty_filter)  # Changed from difficulty to level
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        courses = courses.filter(category_id=category_filter)
    
    # Apply sorting
    sort_by = request.GET.get('sort', '-created_at')
    courses = courses.order_by(sort_by)
    
    # Annotate with additional data
    courses = courses.annotate(
        enrollment_count=Count('enrollments', distinct=True),
        lesson_count=Count('lessons', distinct=True),
        assignment_count=Count('assignments', distinct=True),
        exam_count=Count('exams', distinct=True),
        certificate_count=Count('certificates', distinct=True)
    )
    
    # Pagination
    paginator = Paginator(courses, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics - USING CORRECT FIELD NAMES
    total_courses = Course.objects.count()
    active_courses = Course.objects.filter(published=True).count()  # Changed from is_active to published
    draft_courses = Course.objects.filter(published=False).count()  # Changed from is_published to published
    total_enrollments = Enrollment.objects.count()
    total_certificates = Certificate.objects.count()
    
    # Calculate average rating (you might need to adjust this based on your Review model)
    avg_rating = 4.5
    
    # Additional stats
    total_lessons = Lesson.objects.count()
    total_assignments = Assignment.objects.count()
    total_exams = Exam.objects.count()
    completion_rate = 75
    
    # Categories for filter
    categories = Course.objects.all()
    selected_category = None
    if category_filter:
        selected_category = Category.objects.filter(id=category_filter).first()
    
    context = {
        "courses": page_obj,
        "total_courses": total_courses,
        "active_courses": active_courses,
        "draft_courses": draft_courses,
        "total_enrollments": total_enrollments,
        "total_certificates": total_certificates,
        "avg_rating": avg_rating,
        "total_lessons": total_lessons,
        "total_assignments": total_assignments,
        "total_exams": total_exams,
        "completion_rate": completion_rate,
        "categories": categories,
        "selected_category": selected_category,
    }
    
    return render(request, "admin/course_list.html", context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile, Plan  # assuming you have a Plan model

@login_required
def upgrade_account(request):
    """
    Allows a user to upgrade their subscription plan.
    Shows available plans and disables current plan.
    """
    user_profile = request.user.profile  # assuming OneToOne UserProfile
    current_plan = user_profile.plan if hasattr(user_profile, 'plan') else None
    available_plans = Plan.objects.exclude(id=current_plan.id) if current_plan else Plan.objects.all()

    if request.method == "POST":
        selected_plan_id = request.POST.get("plan")
        try:
            new_plan = Plan.objects.get(id=selected_plan_id)
        except Plan.DoesNotExist:
            messages.error(request, "Selected plan does not exist.")
            return redirect("accounts:upgrade")

        if current_plan and new_plan.id == current_plan.id:
            messages.warning(request, "You are already on this plan.")
            return redirect("accounts:upgrade")

        # Update user's plan
        user_profile.plan = new_plan
        user_profile.save()
        messages.success(request, f"Successfully upgraded to {new_plan.name}!")
        return redirect("accounts:profile_settings")  # redirect back to profile

    context = {
        "current_plan": current_plan,
        "available_plans": available_plans,
    }
    return render(request, "accounts/upgrade_account.html", context)

@login_required
def profile_setting(request):
    profile = request.user.profile

    if request.method == "POST":
        profile.full_name = request.POST.get("full_name")
        profile.phone = request.POST.get("phone")

        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile_settings")

    return render(request, "accounts/profile_settings.html", {
        "profile": profile,
    })

@login_required
def accept_terms(request):
    profile = request.user.profile
    profile.accepted_terms = True
    profile.save()

    messages.success(request, "You have accepted the Terms & Conditions.")
    return redirect("accounts:dashboard")
