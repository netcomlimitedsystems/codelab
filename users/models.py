# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# users/models.py (partial — update UserProfile)
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto')
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    # Preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='auto')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    course_updates = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=True)

    # Security
    last_password_change = models.DateTimeField(auto_now_add=True)
    two_factor_enabled = models.BooleanField(default=False)

    # NEW: email verification flag
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Login Histories"
        ordering = ['-timestamp']
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.user.username} - {self.timestamp} - {status}"

class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('profile_update', 'Profile Updated'),
        ('password_change', 'Password Changed'),
        ('course_enroll', 'Course Enrolled'),
        ('course_complete', 'Course Completed'),
        ('certificate_download', 'Certificate Downloaded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"

# Signals
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # If profile doesn't exist, create it
        UserProfile.objects.create(user=instance)