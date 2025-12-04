from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
User = get_user_model()

# =====================
# CAREERS
# =====================
class Career(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=100, choices=[
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("remote", "Remote"),
    ])
    description = models.TextField()
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =====================
# BLOG CATEGORY
# =====================
class BlogCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =====================
# BLOG POST (Correct Version)
# =====================
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="blog_thumbs/", null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# =====================
# BLOG COMMENTS
# =====================
class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name}"


# =====================
# USER PROFILE
# =====================
class Profile(models.Model):
    """
    Extended user profile with points system
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    updated = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    accepted_terms = models.BooleanField(default=False)

    # Gamification
    points = models.IntegerField(default=0)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Daily streak tracking
    last_login_date = models.DateField(null=True, blank=True)
    consecutive_login_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def level(self):
        """User level increases every 100 points"""
        return self.points // 100 + 1

    @property
    def progress_to_next_level(self):
        """Percentage progress to next level"""
        current_level_points = (self.level - 1) * 100
        points_in_level = self.points - current_level_points
        return min(100, (points_in_level / 100) * 100)


# =====================
# PLANS
# =====================
class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.CharField(max_length=50, help_text="e.g., '1 month', '1 year'")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
