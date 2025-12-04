from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson, Assignment, AssignmentSubmission, Exam, ExamQuestion, ExamSubmission, Enrollment, Certificate
from django.contrib import messages
from .utils import send_certificate_email

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from courses.models import Course
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Review  # Make sure you have a Review model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Review  # make sure Review is imported

@login_required
def submit_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        # Validate rating
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating. Please select a value between 1 and 5.")
            return redirect('courses:course_detail', slug=course.slug)

        # Check if user already reviewed
        existing_review = Review.objects.filter(course=course, user=request.user).first()
        if existing_review:
            messages.error(request, "You have already submitted a review for this course.")
            return redirect('courses:course_detail', slug=course.slug)

        # Save review
        Review.objects.create(
            course=course,
            user=request.user,
            rating=rating,
            comment=comment
        )

        messages.success(request, "Thank you! Your review has been submitted.")
        return redirect('courses:course_detail', slug=course.slug)

    # If GET request, redirect back
    return redirect('courses:course_detail', slug=course.slug)


def catalog(request):
    q = request.GET.get("q")
    filter_type = request.GET.get("filter")

    courses = Course.objects.filter(published=True)

    if q:
        courses = courses.filter(title__icontains=q)

    if filter_type == "free":
        courses = courses.filter(is_paid=False)
    elif filter_type == "paid":
        courses = courses.filter(is_paid=True)
    elif filter_type in ["beginner", "intermediate", "advanced"]:
        courses = courses.filter(level=filter_type)

    return render(request, "pages/catalog.html", {"courses": courses})


def staff_required(view_func):
    """Decorator to ensure user is staff or superuser"""
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url='/accounts/login/'
    )
    return actual_decorator(view_func)
def view_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk, user=request.user)
    return render(request, "courses/view_certificate.html", {"cert": cert})
from django.http import FileResponse

def download_certificate(request, pk):
    cert = get_object_or_404(Certificate, pk=pk, user=request.user)
    return FileResponse(cert.file.open("rb"), as_attachment=True, filename=cert.filename)

@login_required
def my_courses(request):
    # Get all enrollments of the user
    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")

    courses_progress = []

    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = course.lessons.count()
        completed_lessons = LessonCompletion.objects.filter(
            user=request.user,
            lesson__course=course
        ).count()

        progress = round((completed_lessons / total_lessons) * 100) if total_lessons else 0

        courses_progress.append({
            "course": course,
            "enrollment": enrollment,
            "progress": progress,
        })

    return render(request, "courses/my_courses.html", {
        "courses_progress": courses_progress
    })
def course_list(request):
    # Base queryset - show only published courses to regular users
    if request.user.is_staff or request.user.is_superuser:
        # Staff can see all courses, including drafts
        courses = Course.objects.all()
        
        # Check if drafts should be shown (for admin view)
        show_drafts = request.GET.get('drafts') == '1'
        if not show_drafts:
            courses = courses.filter(published=True)
    else:
        # Regular users only see published courses
        courses = Course.objects.filter(published=True)
        show_drafts = False
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Level filter
    level_filter = request.GET.get('level', '')
    if level_filter:
        courses = courses.filter(level=level_filter)
    
    # Calculate statistics for admin users
    published_count = draft_count = featured_count = 0
    if request.user.is_staff or request.user.is_superuser:
        published_count = Course.objects.filter(published=True).count()
        draft_count = Course.objects.filter(published=False).count()
        featured_count = Course.objects.filter(featured=True).count()
    
    # Get enrolled courses for the current user to show progress
    enrolled_course_ids = []
    user_progress = {}
    
    if request.user.is_authenticated:
        user_enrollments = Enrollment.objects.filter(student=request.user)
        enrolled_course_ids = list(user_enrollments.values_list('course_id', flat=True))
        
        # Calculate progress for each enrolled course
        for course_id in enrolled_course_ids:
            course = Course.objects.get(id=course_id)
            total_lessons = course.lessons.count()
            if total_lessons > 0:
                completed_lessons = LessonCompletion.objects.filter(
                    user=request.user,
                    lesson__course=course
                ).count()
                user_progress[course_id] = int((completed_lessons / total_lessons) * 100)
            else:
                user_progress[course_id] = 0
    
    # Add progress information to courses
    for course in courses:
        course.user_progress = user_progress.get(course.id, 0)
    
    # Pagination
    paginator = Paginator(courses, 9)  # Show 9 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'enrolled_course_ids': enrolled_course_ids,
        'search_query': search_query,
        'level_filter': level_filter,
        'show_drafts': show_drafts,
        'published_count': published_count,
        'draft_count': draft_count,
        'featured_count': featured_count,
    }
    
    return render(request, "courses/course_list.html", context)
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from courses.models import Course, LessonCompletion, Enrollment, Review

def course_detail(request, slug):
    # Fetch the course
    course = get_object_or_404(Course, slug=slug)
    
    # Related objects
    lessons = course.lessons.all()
    assignments = course.assignments.all()
    exams = course.exams.all()
    
    enrolled = False
    progress = 0
    completed_lessons = []
    current_lesson = None  # for the "Continue Learning" button

    # Reviews
    rating_breakdown = []
    average_rating = 0
    total_reviews = 0

    if request.user.is_authenticated:
        # Check if user is enrolled
        enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()

        if enrolled and lessons.exists():
            # Completed lessons
            completed_lessons = LessonCompletion.objects.filter(
                user=request.user,
                lesson__in=lessons
            ).values_list('lesson_id', flat=True)

            # Progress calculation
            total_lessons = lessons.count()
            completed_count = len(completed_lessons)
            progress = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0

            # Mark lessons as completed in queryset
            for lesson in lessons:
                lesson.completed = lesson.id in completed_lessons

            # Determine the next lesson to continue
            for lesson in lessons:
                if lesson.id not in completed_lessons:
                    current_lesson = lesson
                    break
            # If all lessons completed, use the first lesson
            if not current_lesson:
                current_lesson = lessons.first()
    else:
        # For anonymous users, just set the first lesson as current
        if lessons.exists():
            current_lesson = lessons.first()

    # Reviews: calculate dynamically from database
    reviews = Review.objects.filter(course=course)
    total_reviews = reviews.count()
    if total_reviews > 0:
        average_rating = reviews.aggregate(avg=Avg('rating'))['avg']
        # Rating breakdown
        rating_counts = reviews.values('rating').annotate(count=Count('id')).order_by('-rating')
        rating_breakdown = [(f"{r['rating']} stars", r['count']) for r in rating_counts]
    else:
        # fallback if no reviews
        rating_breakdown = [("5 stars", 0), ("4 stars", 0), ("3 stars", 0), ("2 stars", 0), ("1 star", 0)]

    return render(request, "courses/course_detail.html", {
        "course": course,
        "lessons": lessons,
        "assignments": assignments,
        "exams": exams,
        "enrolled": enrolled,
        "progress": progress,
        "completed_lessons": completed_lessons,
        "current_lesson": current_lesson,
        "rating_breakdown": rating_breakdown,
        "average_rating": average_rating,
        "total_reviews": total_reviews,
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import LessonCompletion

@login_required
@require_POST
def mark_lesson_complete(request, course_slug, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course__slug=course_slug)
    
    # Check if user is enrolled in the course
    enrolled = Enrollment.objects.filter(
        course=lesson.course, 
        student=request.user
    ).exists()
    
    if not enrolled:
        return JsonResponse({'success': False, 'error': 'Not enrolled in this course'})
    
    # Create or get completion record
    completion, created = LessonCompletion.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    # Calculate new progress
    course_lessons = lesson.course.lessons.all()
    completed_count = LessonCompletion.objects.filter(
        user=request.user,
        lesson__in=course_lessons
    ).count()
    total_lessons = course_lessons.count()
    progress = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 0
    
    return JsonResponse({
        'success': True,
        'completed': True,
        'progress': progress,
        'completed_count': completed_count,
        'total_lessons': total_lessons
    })
# -----------------------------
# Enroll in a course
# -----------------------------
def enroll_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    # -----------------------------
    # User is logged in
    # -----------------------------
    if request.user.is_authenticated:
        # Already enrolled
        if Enrollment.objects.filter(course=course, student=request.user).exists():
            messages.info(request, f"You are already enrolled in {course.title}.")
            return redirect(course.get_absolute_url())

        # Free course → enroll directly
        if not course.is_paid:
            Enrollment.objects.create(course=course, student=request.user)
            messages.success(request, f"You have been enrolled in the free course: {course.title}")
            return redirect(course.get_absolute_url())

        # Paid course → store in session and redirect to payment selection
        request.session['course_to_pay'] = course.id
        return redirect('courses:pay_course', course_slug=course.slug)

    # -----------------------------
    # User is NOT logged in
    # -----------------------------
    else:
        # Store next URL for redirect after login
        next_url = reverse('courses:enroll_course', args=[course.slug])
        messages.info(request, "Please login or register to enroll in this course.")
        return redirect(f"{reverse('accounts:login')}?next={next_url}")






# -----------------------------
# Lesson Detail
# -----------------------------
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)
    lessons = course.lessons.all()
    
    # Check enrollment
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()
    
    if not enrolled:
        return redirect('courses:course_detail', slug=course_slug)
    
    # Get next and previous lessons
    next_lesson = lessons.filter(order__gt=lesson.order).first()
    previous_lesson = lessons.filter(order__lt=lesson.order).last()
    
    # Check if lesson is completed
    completed = False
    if request.user.is_authenticated:
        completed = LessonCompletion.objects.filter(
            user=request.user,
            lesson=lesson
        ).exists()
    
    context = {
        'course': course,
        'lesson': lesson,
        'lessons': lessons,
        'next_lesson': next_lesson,
        'previous_lesson': previous_lesson,
        'completed': completed,
        'enrolled': enrolled,
    }
    
    return render(request, 'courses/lesson_detail.html', context)

# -----------------------------
# Assignment Detail & Submission
# -----------------------------
@login_required
def assignment_detail(request, course_slug, assignment_id):
    course = get_object_or_404(Course, slug=course_slug)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    submitted = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()

    if request.method == "POST":
        file = request.FILES.get("file")
        text = request.POST.get("text_answer", "")
        submission, created = AssignmentSubmission.objects.get_or_create(assignment=assignment, student=request.user)
        if file:
            submission.file = file
        submission.text_answer = text
        submission.save()
        messages.success(request, "Assignment submitted successfully!")
        return redirect(assignment.get_absolute_url())

    return render(request, "courses/assignment_detail.html", {
        "course": course,
        "assignment": assignment,
        "submitted": submitted
    })

# -----------------------------
# Exam Detail & Submission
# -----------------------------
@login_required
def exam_detail(request, course_slug, exam_id):
    course = get_object_or_404(Course, slug=course_slug)
    exam = get_object_or_404(Exam, id=exam_id, course=course)
    questions = exam.questions.all()
    submission = ExamSubmission.objects.filter(exam=exam, student=request.user).first()
    
    if request.method == "POST" and not submission:
        total_score = 0
        # Calculate total score
        for q in questions:
            ans = request.POST.get(str(q.id))
            if ans == q.correct_choice:
                total_score += q.points

        passed = total_score >= exam.pass_mark
        submission = ExamSubmission.objects.create(
            exam=exam, student=request.user, score=total_score, passed=passed
        )

        # -----------------------------
        # Issue Certificate if passed
        # -----------------------------
        if passed:
            cert, created = Certificate.objects.get_or_create(user=request.user, course=course)
            if created:
                # Generate QR code & PDF
                cert.generate_qr()
                cert.generate_pdf()
                cert.save()
                # Send certificate by email
                try:
                    send_certificate_email(request.user, cert)
                except Exception as e:
                    print("Certificate email error:", e)

        messages.success(request, f"Exam submitted. Score: {total_score}. Passed: {passed}")
        return redirect(exam.get_absolute_url())

    return render(request, "courses/exam_detail.html", {
        "course": course,
        "exam": exam,
        "questions": questions,
        "submission": submission
    })

# -----------------------------
# Certificates
# -----------------------------
@login_required
def my_certificates(request):
    certificates = Certificate.objects.filter(user=request.user)
    return render(request, "courses/certificates.html", {"certificates": certificates})
# -----------------------------
# Payment page for paid courses
# -----------------------------
# Example: You may have helper modules to interact with payment APIs
from payments.m_pesa import mpesa_pay, verify_mpesa_payment
from payments.paypal import paypal_create_order, paypal_capture_order
from payments.stripe import stripe_create_session, stripe_verify_payment

@login_required
def pay_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    # -----------------------------
    # Free course → enroll directly
    # -----------------------------
    if not course.is_paid:
        Enrollment.objects.get_or_create(course=course, student=request.user)
        messages.info(request, "This course is free. You have been enrolled.")
        return redirect(course.get_absolute_url())

    # -----------------------------
    # Paid course
    # -----------------------------
    # Store course in session for return after payment
    request.session['course_to_pay'] = course.id

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # -----------------------------
        # M-Pesa Payment
        # -----------------------------
        if payment_method == "mpesa":
            phone_number = request.POST.get("phone_number")
            # Initiate M-Pesa payment (STK Push)
            response = mpesa_pay(phone_number, course.price, course.id, request.user.id)
            if response.get("success"):
                messages.info(request, "M-Pesa payment initiated. Complete the payment on your phone.")
            else:
                messages.error(request, f"M-Pesa Error: {response.get('message')}")
            return redirect(course.get_absolute_url())

        # -----------------------------
        # PayPal Payment
        # -----------------------------
        elif payment_method == "paypal":
            # Create PayPal order and get approval URL
            order = paypal_create_order(course.price, request.user.email, course.id)
            return redirect(order['approval_url'])

        # -----------------------------
        # Stripe Payment
        # -----------------------------
        elif payment_method == "stripe":
            session = stripe_create_session(course.price, request.user.email, course.id)
            return redirect(session.url)

        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect(course.get_absolute_url())

    return render(request, "courses/pay_course.html", {"course": course})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from courses.models import Course, Enrollment

# Payment helpers (mocked / stubbed)
from payments.m_pesa import mpesa_pay, verify_mpesa_payment
from payments.paypal import paypal_create_order, paypal_capture_order
from payments.stripe import stripe_create_session, stripe_verify_payment


@login_required
def pay_course(request, course_slug):
    """
    Handles payment for paid courses via M-Pesa, PayPal, or Stripe.
    Auto-enrolls user after successful payment.
    """
    course = get_object_or_404(Course, slug=course_slug)

    # -----------------------------
    # Free course → enroll immediately
    # -----------------------------
    if not course.is_paid:
        Enrollment.objects.get_or_create(course=course, student=request.user)
        messages.success(request, "This course is free. You have been enrolled.")
        return redirect(course.get_absolute_url())

    # -----------------------------
    # Store course in session for payment callbacks
    # -----------------------------
    request.session['course_to_pay'] = course.id

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # -----------------------------
        # M-Pesa Payment
        # -----------------------------
        if payment_method == "mpesa":
            phone_number = request.POST.get("phone_number")
            if not phone_number:
                messages.error(request, "Phone number is required for M-Pesa payment.")
                return redirect(course.get_absolute_url())

            response = mpesa_pay(phone_number, course.price, course.id, request.user.id)
            if response.get("success"):
                messages.info(request, "M-Pesa payment initiated. Complete it on your phone.")
            else:
                messages.error(request, f"M-Pesa Error: {response.get('message')}")
            return redirect(course.get_absolute_url())

        # -----------------------------
        # PayPal Payment
        # -----------------------------
        elif payment_method == "paypal":
            order = paypal_create_order(course.price, request.user.email, course.id)
            return redirect(order['approval_url'])

        # -----------------------------
        # Stripe Payment
        # -----------------------------
        elif payment_method == "stripe":
            session = stripe_create_session(course.price, request.user.email, course.id)
            return redirect(session.url)

        # -----------------------------
        # Invalid method
        # -----------------------------
        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect(course.get_absolute_url())

    return render(request, "courses/pay_course.html", {"course": course})


# -----------------------------
# Payment Verification Endpoints
# -----------------------------

@login_required
def verify_mpesa(request):
    transaction_id = request.GET.get("transaction_id")
    course_id = request.GET.get("course_id")
    if not transaction_id or not course_id:
        messages.error(request, "Invalid M-Pesa verification request.")
        return redirect('courses:dashboard')

    if verify_mpesa_payment(transaction_id, request.user.id, course_id):
        course = get_object_or_404(Course, id=course_id)
        Enrollment.objects.get_or_create(course=course, student=request.user)
        messages.success(request, f"M-Pesa payment confirmed! You are now enrolled in {course.title}")
    else:
        messages.error(request, "M-Pesa payment verification failed.")

    return redirect('courses:dashboard')


@login_required
def verify_paypal(request):
    order_id = request.GET.get("order_id")
    course_id = request.GET.get("course_id")
    if not order_id or not course_id:
        messages.error(request, "Invalid PayPal verification request.")
        return redirect('courses:dashboard')

    if paypal_capture_order(order_id):
        course = get_object_or_404(Course, id=course_id)
        Enrollment.objects.get_or_create(course=course, student=request.user)
        messages.success(request, f"PayPal payment confirmed! You are now enrolled in {course.title}")
    else:
        messages.error(request, "PayPal payment failed.")

    return redirect('courses:dashboard')


@login_required
def verify_stripe(request):
    session_id = request.GET.get("session_id")
    course_id = request.GET.get("course_id")
    if not session_id or not course_id:
        messages.error(request, "Invalid Stripe verification request.")
        return redirect('courses:dashboard')

    if stripe_verify_payment(session_id):
        course = get_object_or_404(Course, id=course_id)
        Enrollment.objects.get_or_create(course=course, student=request.user)
        messages.success(request, f"Stripe payment confirmed! You are now enrolled in {course.title}")
    else:
        messages.error(request, "Stripe payment verification failed.")

    return redirect('courses:dashboard')
