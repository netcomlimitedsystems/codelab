from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Forum, Discussion, Comment
from .forms import DiscussionForm, CommentForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Max
from .models import Discussion
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Forum,UserScore
from .forms import ForumForm
# views.py
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Updated leaderboard view in views.py
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib.auth import get_user_model
 
 # Weekly Leaderboard
def weekly_leaderboard(request):
    top_users = PointTransaction.objects.order_by('-points')[:10]  # adjust 'score' and model
    return render(request, 'community/weekly_leaderboard.html', {'top_users': top_users})
def points_system(request):
    """
    Display how points are earned in the community.
    """
    points_rules = [
        {"action": "Create a post", "points": 10},
        {"action": "Comment on a post", "points": 5},
        {"action": "Receive an upvote", "points": 2},
        {"action": "Complete a course", "points": 20},
    ]
    return render(request, 'community/points_system.html', {'points_rules': points_rules})
# Daily Leaderboard (if needed)
def daily_leaderboard(request):
    top_users = PointTransaction.objects.order_by('-points')[:10]  # example
    return render(request, 'community/daily_leaderboard.html', {'top_users': top_users})
def guidelines(request):
    return render(request, 'community/guidelines.html')
def forum_list(request):
    forums = Forum.objects.all()
    return render(request, 'community/', {'forums': forums})
from .models import Achievement  # optional, if you track achievements

def achievements(request):
    # Example: get all achievements or user-specific achievements
    user_achievements = Achievement.objects.all()  # replace with user filter if needed
    return render(request, 'community/achievements.html', {'achievements': user_achievements})
def user_profile(request, user_id):
    """Simple user profile view"""
    User = get_user_model()
    profile_user = get_object_or_404(User, id=user_id)
    
    # Get user statistics
    discussion_count = profile_user.discussion_set.count()
    comment_count = profile_user.comment_set.count()
    total_posts = discussion_count + comment_count
    
    context = {
        'profile_user': profile_user,
        'discussion_count': discussion_count,
        'comment_count': comment_count,
        'total_posts': total_posts,
    }
    
    return render(request, 'community/user_profile.html', context)
def leaderboard(request):
    # Get all users with profiles, ordered by points
    users = User.objects.select_related('profile').all()
    
    # Calculate statistics
    total_users = users.count()
    
    # Active users today (users who logged in today)
    today = timezone.now().date()
    active_users_today = users.filter(
        last_login__date=today
    ).count()
    
    # Total points
    total_points = users.aggregate(
        total_points=Sum('profile__points')
    )['total_points'] or 0
    
    # Average points
    avg_points = users.aggregate(
        avg_points=Avg('profile__points')
    )['avg_points'] or 0
    avg_points = round(avg_points, 1)
    
    # Prepare users data for JSON
    users_data = []
    sorted_users = sorted(users, key=lambda u: u.profile.points or 0, reverse=True)
    
    for idx, user in enumerate(sorted_users, start=1):
        profile = user.profile
        
        # Get post count
        post_count = user.discussion_set.count() + user.comment_set.count()
        
        # Profile picture URL
        profile_picture = None
        if profile.profile_picture and hasattr(profile.profile_picture, 'url'):
            profile_picture = profile.profile_picture.url
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'profile': {
                'full_name': profile.full_name or '',
                'points': profile.points or 0,
            },
            'profile_picture': profile_picture,
            'post_count': post_count,
            'points_today': 0,
            'rank': idx,
        })
    
    # Get top contributors (users with most posts)
    top_contributors = sorted(
        users, 
        key=lambda u: u.discussion_set.count() + u.comment_set.count(), 
        reverse=True
    )[:5]
    
    # Time periods for the template
    time_periods = [
        {'value': 'today', 'label': 'Today', 'icon': 'fa-calendar-day'},
        {'value': 'week', 'label': 'This Week', 'icon': 'fa-calendar-week'},
        {'value': 'month', 'label': 'This Month', 'icon': 'fa-calendar-alt'},
        {'value': 'all-time', 'label': 'All Time', 'icon': 'fa-history'}
    ]
    
    # Recent achievements (if you have an Achievement model)
    recent_achievements = []
    try:
        from .models import Achievement
        recent_achievements = Achievement.objects.select_related('user').order_by('-created_at')[:5]
    except:
        pass
    
    # Pagination
    paginator = Paginator(sorted_users[:100], 20)  # Show top 100 users, 20 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'users_json': json.dumps(users_data, default=str),
        'total_users': total_users,
        'active_users_today': active_users_today,
        'total_points': total_points,
        'avg_points': avg_points,
        'top_contributors': top_contributors,
        'recent_achievements': recent_achievements,
        'time_periods': time_periods,
    }
    
    return render(request, 'community/leaderboard.html', context)

@csrf_exempt
def api_leaderboard(request, period):
    """API endpoint for period-based leaderboard"""
    try:
        # Get all users
        users = User.objects.select_related('profile').all()
        
        # Filter by period if needed
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            # For now, return all users since we don't track daily points
            # In a real app, you'd filter by activity in this period
            filtered_users = users
        elif period == 'week':
            start_date = now - timedelta(days=7)
            filtered_users = users
        elif period == 'month':
            start_date = now - timedelta(days=30)
            filtered_users = users
        else:  # all-time
            filtered_users = users
        
        # Prepare response data
        users_data = []
        sorted_users = sorted(filtered_users, key=lambda u: u.profile.points or 0, reverse=True)
        
        for idx, user in enumerate(sorted_users, start=1):
            profile = user.profile
            
            # Profile picture URL
            profile_picture = None
            if profile.profile_picture and hasattr(profile.profile_picture, 'url'):
                profile_picture = profile.profile_picture.url
            
            users_data.append({
                'id': user.id,
                'username': user.username,
                'profile': {
                    'full_name': profile.full_name or '',
                    'points': profile.points or 0,
                },
                'profile_picture': profile_picture,
                'post_count': user.discussion_set.count() + user.comment_set.count(),
                'rank': idx,
            })
        
        # Calculate stats
        stats = {
            'total_users': len(users_data),
            'active_users': len(users_data),
            'total_points': sum(user['profile']['points'] for user in users_data),
            'avg_points': sum(user['profile']['points'] for user in users_data) / len(users_data) if users_data else 0,
        }
        
        return JsonResponse({
            'users': users_data,
            'stats': stats,
            'period': period,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def staff_required(function=None):
    """
    Decorator for views that checks if the user is staff or superuser.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url='/admin/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

@login_required
@staff_required
def create_forum(request):
    """
    Create a new forum (staff/superuser only)
    """
    if request.method == 'POST':
        form = ForumForm(request.POST)
        if form.is_valid():
            forum = form.save(commit=False)
            forum.author = request.user
            forum.save()
            messages.success(request, f'Forum "{forum.name}" created successfully!')
            return redirect('community:forum_detail', forum_slug=forum.slug)
    else:
        form = ForumForm()
    
    context = {
        'form': form,
        'title': 'Create New Forum'
    }
    return render(request, 'community/forum_form.html', context)

@login_required
@staff_required
def edit_forum(request, forum_slug):
    """
    Edit an existing forum (staff/superuser only)
    """
    forum = get_object_or_404(Forum, slug=forum_slug)
    
    if request.method == 'POST':
        form = ForumForm(request.POST, instance=forum)
        if form.is_valid():
            forum = form.save()
            messages.success(request, f'Forum "{forum.name}" updated successfully!')
            return redirect('community:forum_detail', forum_slug=forum.slug)
    else:
        form = ForumForm(instance=forum)
    
    context = {
        'form': form,
        'forum': forum,
        'title': f'Edit Forum: {forum.name}'
    }
    return render(request, 'community/forum_form.html', context)

@login_required
@staff_required
def delete_forum(request, forum_slug):
    """
    Delete a forum (staff/superuser only)
    """
    forum = get_object_or_404(Forum, slug=forum_slug)
    
    if request.method == 'POST':
        forum_name = forum.name
        forum.delete()
        messages.success(request, f'Forum "{forum_name}" deleted successfully!')
        return redirect('community:index')
    
    context = {
        'forum': forum
    }
    return render(request, 'community/forum_confirm_delete.html', context)

@login_required
@staff_required
def manage_forums(request):
    """
    Forum management dashboard for staff/superusers
    """
    forums = Forum.objects.all().select_related('author').prefetch_related('discussions')
    
    # Statistics
    total_forums = forums.count()
    active_forums = forums.filter(is_active=True).count()
    inactive_forums = forums.filter(is_active=False).count()
    total_discussions = sum(forum.discussions.count() for forum in forums)
    
    context = {
        'forums': forums,
        'total_forums': total_forums,
        'active_forums': active_forums,
        'inactive_forums': inactive_forums,
        'total_discussions': total_discussions,
    }
    return render(request, 'community/manage_forums.html', context)

@login_required
def add_comment(request, discussion_id):
    """
    Handles adding a comment or reply to a discussion.
    Supports nested replies using parent_id.
    """
    discussion = get_object_or_404(Discussion, id=discussion_id)

    if request.method == "POST":
        content = request.POST.get('body', '').strip()
        parent_id = request.POST.get('parent_id')
        parent_comment = None

        # If replying to a comment, fetch parent
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, discussion=discussion)
            except Comment.DoesNotExist:
                parent_comment = None

        if content:
            Comment.objects.create(
                discussion=discussion,
                author=request.user,
                content=content,
                parent=parent_comment
            )
            messages.success(request, "Your comment has been posted!")
        else:
            messages.error(request, "Comment cannot be empty.")

    return redirect('community:discussion_detail', discussion_id=discussion.id)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Comment, CommentLike

@login_required
def toggle_comment_like(request, comment_id):
    """
    Like or unlike a comment. Returns JSON with new like count.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    # Check if the user has already liked
    existing_like = CommentLike.objects.filter(comment=comment, user=user).first()

    if existing_like:
        # Unlike
        existing_like.delete()
        liked = False
    else:
        # Like
        CommentLike.objects.create(comment=comment, user=user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'like_count': comment.likes.count()
    })

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()  # toggle unlike
    return redirect('community:discussion_detail', discussion_id=comment.discussion.id)


def all_discussions(request):
    discussions = Discussion.objects.all()
    return render(request, "community/all_discussions.html", {"discussions": discussions})


def community_index(request):
    """Main community page showing forums"""
    forums = Forum.objects.filter(is_active=True).prefetch_related('discussions')

    
    # Get recent discussions across all forums, including author profiles
    recent_discussions = Discussion.objects.filter(
        forum__is_active=True
    ).select_related('forum', 'author', 'author__profile').order_by('-created_at')[:10]
    
    context = {
        'forums': forums,
        'recent_discussions': recent_discussions,
        'total_discussions': Discussion.objects.count(),
        'total_comments': Comment.objects.count(),
    }
    return render(request, 'community/community.html', context)

@login_required
def forum_detail(request, forum_slug):
    """Show discussions in a specific forum"""
    forum = get_object_or_404(Forum, slug=forum_slug, is_active=True)
    discussions = forum.discussions.all().select_related('author', 'author__profile').order_by('-is_pinned', '-created_at')
    
    # Pagination
    paginator = Paginator(discussions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.forum = forum
            discussion.author = request.user
            discussion.save()
            messages.success(request, 'Discussion started successfully!')
            return redirect('community:forum_detail', forum_slug=forum.slug)
    else:
        form = DiscussionForm()
    
    context = {
        'forum': forum,
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'community/forum_detail.html', context)

from django.db.models import Prefetch

@login_required
def discussion_detail(request, discussion_id):
    discussion = get_object_or_404(
        Discussion.objects.select_related('author', 'author__profile', 'forum'),
        id=discussion_id,
        forum__is_active=True
    )

    # Prefetch comments and replies efficiently
    comments_qs = Comment.objects.filter(parent__isnull=True).select_related('author', 'author__profile').prefetch_related(
        Prefetch('replies', queryset=Comment.objects.select_related('author', 'author__profile'))
    )

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            comment = form.save(commit=False)
            comment.discussion = discussion
            comment.author = request.user
            if parent_id:
                comment.parent_id = int(parent_id)
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('community:discussion_detail', discussion_id=discussion.id)
    else:
        form = CommentForm()

    # Update view count
    discussion.views += 1
    discussion.save(update_fields=['views'])

    context = {
        'discussion': discussion,
        'comments': comments_qs,
        'form': form,
    }
    return render(request, 'community/discussion_detail.html', context)


from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Forum, Discussion
from .forms import DiscussionForm

@login_required
def create_discussion(request, forum_slug=None):
    """
    Create a new discussion in a given forum.
    If forum_slug is invalid or inactive, show an error instead of 404.
    """
    forum = None
    if forum_slug:
        try:
            forum = Forum.objects.get(slug=forum_slug, is_active=True)
        except Forum.DoesNotExist:
            messages.error(request, f"The forum '{forum_slug}' does not exist or is inactive.")
            return redirect('community:index')  # Redirect to forum list or homepage

    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.forum = forum
            discussion.author = request.user
            discussion.save()
            messages.success(request, 'Discussion created successfully!')
            return redirect('community:discussion_detail', discussion_id=discussion.id)
    else:
        form = DiscussionForm()

    context = {
        'forum': forum,
        'form': form,
    }
    return render(request, 'community/create_discussion.html', context)


@login_required
def search_discussions(request):
    """Search discussions with author profiles"""
    query = request.GET.get('q', '')
    discussions = Discussion.objects.none()
    
    if query:
        discussions = Discussion.objects.filter(
            title__icontains=query
        ).select_related('forum', 'author', 'author__profile').order_by('-created_at')
    
    context = {
        'discussions': discussions,
        'query': query,
        'results_count': discussions.count(),
    }
    return render(request, 'community/search_results.html', context)



@login_required
def edit_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)

    # Permission check
    if request.user != discussion.author and not request.user.is_staff:
        return redirect('community:discussion_detail', discussion_id=pk)

    if request.method == 'POST':
        form = DiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            return redirect('community:discussion_detail', discussion_id=pk)
    else:
        form = DiscussionForm(instance=discussion)

    return render(request, 'community/edit_discussion.html', {
        'form': form,
        'discussion': discussion
    })


@login_required
def delete_discussion(request, pk):
    discussion = get_object_or_404(Discussion, pk=pk)

    # Only author or staff can delete
    if request.user != discussion.author and not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this discussion.")
        return redirect('community:discussion_detail', pk=pk)

    if request.method == "POST":
        discussion.delete()
        messages.success(request, "Discussion deleted successfully.")
        return redirect('community:index')

    # Optional: render a confirmation page
    return render(request, 'community/delete_discussion_confirm.html', {'discussion': discussion})


@login_required
def my_discussions(request):
    """Show user's discussions with profile info and sidebar insights"""

    # Discussions by logged-in user
    discussions = (
        Discussion.objects.filter(author=request.user)
        .select_related('forum', 'author', 'author__profile')
        .prefetch_related('comments')
        .annotate(total_comments=Count('comments'))
        .order_by('-created_at')
    )

    # Total comments across all discussions
    total_comments = sum(d.total_comments for d in discussions)

    # Total views
    total_views = sum(d.views for d in discussions)

    # Sidebar insights
    most_active_discussion = discussions.order_by('-total_comments').first()
    most_viewed_discussion = discussions.order_by('-views').first()
    latest_discussion = discussions.order_by('-created_at').first()

    # Fetch forums for "New Discussion" dropdown
    forums = request.user.forum_set.all()[:10]

    context = {
        'discussions': discussions,
        'total_comments': total_comments,
        'total_views': total_views,
        'most_active_discussion': most_active_discussion,
        'most_viewed_discussion': most_viewed_discussion,
        'latest_discussion': latest_discussion,
        'forums': forums,
    }
    return render(request, 'community/my_discussions.html', context)

@login_required
def add_comment(request, discussion_id):
    discussion = get_object_or_404(Discussion, id=discussion_id)
    if request.method == "POST":
        content = request.POST.get('body')  # form input name
        if content:
            Comment.objects.create(
                discussion=discussion,
                author=request.user,
                content=content
            )
    return redirect('community:discussion_detail', discussion_id=discussion.id)
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Tag, Discussion

def tags_list(request):
    """Enhanced tags view with search, filtering, and sorting"""
    tags = Tag.objects.annotate(
        discussion_count=Count('discussions')
    ).order_by('-discussion_count', 'name')
    
    # Search functionality
    search_query = request.GET.get('q', '')
    if search_query:
        tags = tags.filter(name__icontains=search_query)
    
    # Sorting
    sort_by = request.GET.get('sort', 'popular')
    if sort_by == 'name':
        tags = tags.order_by('name')
    elif sort_by == 'newest':
        tags = tags.order_by('-id')
    
    # Tag filtering - show discussions for a specific tag
    tagged_discussions = None
    selected_tag_slug = request.GET.get('tag')
    selected_tag = None
    
    if selected_tag_slug:
        selected_tag = Tag.objects.filter(slug=selected_tag_slug).first()
        if selected_tag:
            tagged_discussions = Discussion.objects.filter(
                tags=selected_tag
            ).select_related('forum', 'author', 'author__profile').prefetch_related('tags').order_by('-created_at')
    
    # Pagination for tags
    paginator = Paginator(tags, 24)  # 24 tags per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tags': page_obj,
        'tagged_discussions': tagged_discussions,
        'selected_tag': selected_tag,
        'search_query': search_query,
        'sort_by': sort_by,
        'page_obj': page_obj,
    }
    return render(request, "community/tags.html", context)