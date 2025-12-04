from courses.models import Notification

def notifications_context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            # Get unread notifications count
            unread_count = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
            
            # Get recent notifications (last 5)
            recent_notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
            
            context.update({
                'unread_notifications_count': unread_count,
                'recent_notifications': recent_notifications,
            })
        except Exception as e:
            # Fallback if there's any issue
            context.update({
                'unread_notifications_count': 0,
                'recent_notifications': [],
            })
    else:
        context.update({
            'unread_notifications_count': 0,
            'recent_notifications': [],
        })
    
    return context

# context_processors.py
def admin_context(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        from django.contrib.auth.models import User
        from courses.models import Course, Enrollment
        
        active_users_count = User.objects.filter(is_active=True).count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        
        return {
            'active_users_count': active_users_count,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
        }
    return {}