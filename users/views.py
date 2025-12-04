from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, PreferencesForm
from .models import UserProfile, LoginHistory, UserActivity
from courses.models import Enrollment, Course,Assignment
from django.utils import translation
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
# from django.utils.encoding import force_bytes, force_text
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # prevent login until email verified
            user.save()

            # Profile is automatically created by the signal (or ensure)
            profile = get_or_create_user_profile(user)

            # Log the registration as an activity (optional)
            UserActivity.objects.create(
                user=user,
                action='profile_update',
                details='Account created (pending email verification)'
            )

            # Send activation email
            current_site = get_current_site(request)
            mail_subject = 'Activate your CodeLab account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_path = reverse('users:activate', kwargs={'uidb64': uid, 'token': token})
            activation_link = f"{request.scheme}://{current_site.domain}{activation_path}"

            message = render_to_string('users/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
                'domain': current_site.domain,
            })

            email = EmailMessage(
                mail_subject, message, to=[user.email],
                from_email=settings.DEFAULT_FROM_EMAIL
            )
            email.content_subtype = "html"
            try:
                email.send()
            except Exception as e:
                # Optionally log error; still show activation page so user can retry
                print("Email send failed:", e)

            # Show page instructing user to check email
            return render(request, 'users/activation_sent.html', {'email': user.email})
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


# Activation view

def activate(request, uidb64, token):
    """
    Activate user account from email link.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # set profile flag
        profile = get_or_create_user_profile(user)
        profile.email_verified = True
        profile.save()

        # Optionally log activity
        UserActivity.objects.create(
            user=user,
            action='profile_update',
            details='Email verified and account activated'
        )

        # Login the user right away (optional) — here we log them in
        login(request, user)
        messages.success(request, 'Your account has been activated. Welcome to CodeLab!')
        return redirect('users:dashboard')
    else:
        # Invalid link
        return render(request, 'users/activation_invalid.html')


def get_or_create_user_profile(user):
    """Helper function to safely get or create user profile"""
    try:
        # Try to get existing profile
        return UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create new profile if it doesn't exist
        return UserProfile.objects.create(user=user)





@login_required
def profile(request):
    # Ensure user has a profile
    profile_instance = get_or_create_user_profile(request.user)
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'form_type' in request.POST and request.POST['form_type'] == 'preferences':
            # Handle preferences form
            preferences_form = PreferencesForm(request.POST, instance=profile_instance)
            if preferences_form.is_valid():
                preferences_form.save()
                
                # Activate the selected language for this user session
                selected_language = preferences_form.cleaned_data.get('language')
                if selected_language in [lang[0] for lang in settings.LANGUAGES]:
                    translation.activate(selected_language)
                    request.session[translation.LANGUAGE_SESSION_KEY] = selected_language
                
                # Log the activity
                UserActivity.objects.create(
                    user=request.user,
                    action='profile_update',
                    details='User preferences updated'
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                messages.success(request, 'Your preferences have been updated!')
                return redirect('users:profile')
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': preferences_form.errors})
        else:
            # Handle main profile form
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                
                # Log the activity
                UserActivity.objects.create(
                    user=request.user,
                    action='profile_update',
                    details='Personal information updated'
                )
                
                messages.success(request, 'Your profile has been updated!')
                return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile_instance)
        preferences_form = PreferencesForm(instance=profile_instance)
    
    # Get user statistics for enrolled courses
    enrolled_courses = Enrollment.objects.filter(user=request.user)
    total_courses = enrolled_courses.count()
    completed_courses = enrolled_courses.filter(completed=True).count()
    
    # Get recent activity and login history
    recent_activity = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:5]
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'preferences_form': preferences_form,
        'recent_activity': recent_activity,
        'login_history': login_history,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'enrolled_courses': enrolled_courses,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def dashboard(request):
    # Safely get or create user profile
    get_or_create_user_profile(request.user)
    
    try:
        # Get user's enrolled courses
        enrolled_courses = Enrollment.objects.filter(user=request.user).select_related('course')
        in_progress_courses = enrolled_courses.filter(completed=False)
        completed_courses = enrolled_courses.filter(completed=True)
        
        # Calculate total learning hours from enrolled courses
        total_learning_hours = enrolled_courses.aggregate(
            total_hours=Sum('course__duration_hours')
        )['total_hours'] or 0
        
        # Get recently accessed courses (last 3 in-progress courses)
        recent_courses = in_progress_courses.order_by('-enrolled_at')[:3]
        
        # Add some sample data for demonstration
        sample_courses = Course.objects.filter(is_published=True)[:3]
        
        # Get pending assignments for completed courses
        completed_course_list = [e.course for e in completed_courses]
        pending_assignments = Assignment.objects.filter(
            course__in=completed_course_list
        ).exclude(
            submissions__user=request.user
        )
        
        # Log dashboard access
        UserActivity.objects.create(
            user=request.user,
            action='login',
            details='Accessed dashboard'
        )
        
        context = {
            'in_progress_courses': in_progress_courses,
            'completed_courses': completed_courses,
            'recent_courses': recent_courses,
            'total_learning_hours': total_learning_hours,
            'featured_courses': sample_courses,
            'pending_assignments': pending_assignments,  # Add this
        }
        return render(request, 'users/dashboard.html', context)
        
    except Exception as e:
        # If there's any error, provide empty context to avoid template errors
        print(f"Dashboard error: {e}")
        context = {
            'in_progress_courses': Enrollment.objects.none(),
            'completed_courses': Enrollment.objects.none(),
            'recent_courses': Enrollment.objects.none(),
            'total_learning_hours': 0,
            'featured_courses': Course.objects.none(),
            'pending_assignments': Assignment.objects.none(),
        }
        return render(request, 'users/dashboard.html', context)


def terms_and_conditions(request):
    return render(request, 'users/terms.html')


def privacy(request):
    return render(request, 'users/privacy_policy.html')


# Activity log view
@login_required
def activity_log(request):
    activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'users/activity_log.html', {'activities': activities})


# Sessions management view (simplified)
@login_required
def sessions(request):
    # Safely get or create user profile
    get_or_create_user_profile(request.user)
    return render(request, 'users/sessions.html')


# Two-factor setup view (placeholder)
@login_required
def two_factor_setup(request):
    # Safely get or create user profile
    profile = get_or_create_user_profile(request.user)
    
    # Toggle the setting
    profile.two_factor_enabled = not profile.two_factor_enabled
    profile.save()
    
    status = "enabled" if profile.two_factor_enabled else "disabled"
    messages.success(request, f'Two-factor authentication has been {status}.')
    return redirect('users:profile')


# Custom Password Change View to use our template and handle success message
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        
        # Update last password change in profile
        profile = get_or_create_user_profile(self.request.user)
        profile.last_password_change = timezone.now()
        profile.save()
        
        # Log the activity
        UserActivity.objects.create(
            user=self.request.user,
            action='password_change',
            details='Password changed successfully'
        )
        
        return super().form_valid(form)


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'