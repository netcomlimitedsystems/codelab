# community/signals.py
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Discussion, Comment, CommentLike, Achievement

def award_points(user, points, reason):
    """
    Award points to a user and create a point transaction record
    """
    if hasattr(user, 'profile'):
        user.profile.points += points
        user.profile.save()
        
        # Create a point transaction log (optional)
        from .models import PointTransaction
        PointTransaction.objects.create(
            user=user,
            points=points,
            reason=reason
        )
        
        # Check for achievements
        check_achievements(user)
        
        return True
    return False

def check_achievements(user):
    """
    Check and award achievements based on points
    """
    profile = user.profile
    points = profile.points
    
    # Define achievement thresholds
    achievements = [
        (10, 'New Member', 'Welcome to the community!', 'fa-seedling'),
        (50, 'Active Member', '50 points earned', 'fa-leaf'),
        (100, 'Community Contributor', '100 points earned', 'fa-users'),
        (250, 'Discussion Leader', '250 points earned', 'fa-comments'),
        (500, 'Community Star', '500 points earned', 'fa-star'),
        (1000, 'Legendary Member', '1000 points earned', 'fa-crown'),
    ]
    
    for threshold, title, description, icon in achievements:
        if points >= threshold:
            # Check if user already has this achievement
            if not Achievement.objects.filter(user=user, title=title).exists():
                Achievement.objects.create(
                    user=user,
                    title=title,
                    description=description,
                    points=threshold,
                    icon=icon
                )

# Signal for new discussion
@receiver(post_save, sender=Discussion)
def award_discussion_points(sender, instance, created, **kwargs):
    if created:
        award_points(instance.author, 10, f'Created discussion: {instance.title}')

# Signal for new comment
@receiver(post_save, sender=Comment)
def award_comment_points(sender, instance, created, **kwargs):
    if created:
        award_points(instance.author, 5, f'Commented on discussion: {instance.discussion.title}')

# Signal for comment like
@receiver(post_save, sender=CommentLike)
def award_like_points(sender, instance, created, **kwargs):
    if created:
        # Award points to comment author (not the liker)
        award_points(instance.comment.author, 2, f'Received like on comment')
        
        # Also award 1 point to the user who gave the like (optional)
        award_points(instance.user, 1, f'Gave a like to a comment')

# Signal for discussion views (simplified)
def award_view_points(discussion, user):
    if user.is_authenticated and user != discussion.author:
        award_points(discussion.author, 0.1, f'Discussion viewed by others')

# Daily login bonus (you'll need to track daily logins)
@receiver(post_save, sender=User)
def update_last_login(sender, instance, **kwargs):
    # This is a simplified version - you'd need to track daily logins separately
    pass