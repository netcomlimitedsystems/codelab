from django.shortcuts import render
from django.views.generic import TemplateView
from courses.models import Course, Category
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from courses.models import Course
from django.shortcuts import render
from .forms import ContactForm
from django.contrib import messages

class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_courses'] = Course.objects.filter(is_published=True)[:8]
        context['categories'] = Category.objects.all()[:8]
        return context

def about(request):
    return render(request, 'pages/about.html')


home = HomeView.as_view()

def contact(request):
    courses = Course.objects.filter(is_published=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        course_id = request.POST.get('course')
        message_content = request.POST.get('message')
        newsletter = request.POST.get('newsletter')
        
        # Basic validation
        if not all([name, email, subject, message_content]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'pages/contact.html', {'courses': courses})
        
        # Prepare email content
        course_info = ""
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                course_info = f"\n\nRelated Course: {course.title}"
            except Course.DoesNotExist:
                pass
        
        full_message = f"""
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message_content}
        {course_info}
        
        Newsletter Opt-in: {'Yes' if newsletter else 'No'}
        """
        
        # Send email (configure email settings in production)
        try:
            send_mail(
                subject=f'CodeLab Contact: {subject}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],  # Add your contact email in settings
                fail_silently=False,
            )
            
            # Also send confirmation to user
            send_mail(
                subject='Thank you for contacting CodeLab',
                message=f'Hi {name},\n\nThank you for reaching out to CodeLab. We have received your message and will get back to you within 24 hours.\n\nBest regards,\nThe CodeLab Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            messages.success(request, 'Thank you for your message! We will get back to you within 24 hours.')
            return redirect('contact')
            
        except Exception as e:
            messages.error(request, 'Sorry, there was an error sending your message. Please try again later.')
            print(f"Email error: {e}")  # Log the error for debugging
    
    return render(request, 'pages/contact.html', {'courses': courses})