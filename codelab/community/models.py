from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
 
# ======================
# FORUM MODEL
# ======================
class Forum(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('community:forum_detail', kwargs={'forum_slug': self.slug})


# ======================
# TAG MODEL
# ======================
# ======================
# TAG MODEL
# ======================
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
 
    # @property
    # def discussion_count(self):
    #     return self.discussions.count()

    def get_absolute_url(self):
        return reverse('community:tags') + f'?tag={self.slug}'


# ======================
# DISCUSSION MODEL
# ======================
class Discussion(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_pinned = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True, related_name='discussions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Award points for new discussion
        if is_new:
            self.award_creation_points()
    
    def award_creation_points(self):
        """Award points for creating a discussion"""
        if hasattr(self.author, 'profile'):
            self.author.profile.points += 10
            self.author.profile.save()
            
            # Log the transaction
            PointTransaction.objects.create(
                user=self.author,
                points=10,
                reason=f'Created discussion: {self.title}'
            )
    
    def get_absolute_url(self):
        return reverse('community:discussion_detail', kwargs={'discussion_id': self.id})

    @property
    def comment_count(self):
        return self.comments.count()


# ======================
# COMMENT MODEL (With Replies)
# ======================
class Comment(models.Model):
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    # REPLY SUPPORT
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username}"
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Award points for new comment
        if is_new:
            self.award_creation_points()
    
    def award_creation_points(self):
        """Award points for creating a comment"""
        if hasattr(self.author, 'profile'):
            self.author.profile.points += 5
            self.author.profile.save()
            
            PointTransaction.objects.create(
                user=self.author,
                points=5,
                reason=f'Commented on discussion: {self.discussion.title}'
            )
    @property
    def like_count(self):
        return self.likes.count()


# ======================
# COMMENT LIKE MODEL
# ======================
class CommentLike(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Award points for new like
        if is_new:
            self.award_points()
    
    def award_points(self):
        """Award points for liking a comment"""
        # Award to comment author
        if hasattr(self.comment.author, 'profile'):
            self.comment.author.profile.points += 2
            self.comment.author.profile.save()
            
            PointTransaction.objects.create(
                user=self.comment.author,
                points=2,
                reason=f'Received like on comment'
            )
        
        # Optional: Award 1 point to the user who gave the like
        if hasattr(self.user, 'profile'):
            self.user.profile.points += 1
            self.user.profile.save()
            
            PointTransaction.objects.create(
                user=self.user,
                points=1,
                reason=f'Gave a like to a comment'
            )
class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, default='fa-trophy')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']




# Add to your community/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PointTransaction(models.Model):
    """
    Track all point transactions for audit trail
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    points = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.points} points - {self.reason}"


class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField(default=0)
    # Optional: track date for weekly/daily filtering
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']  # default ordering by highest score

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.score}"
