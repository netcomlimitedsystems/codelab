from django.urls import path
from . import views

app_name = "community"
from django.http import JsonResponse

def dummy_tracker(request):
    return JsonResponse({"status": "ignored"})

urlpatterns = [
    path("hybridaction/zybTrackerStatisticsAction", dummy_tracker),
    path("", views.community_index, name="index"),
    
    # Forum management URLs
    path("forum/create/", views.create_forum, name="create_forum"),
    path("forum/<slug:forum_slug>/edit/", views.edit_forum, name="edit_forum"),
    path("forum/<slug:forum_slug>/delete/", views.delete_forum, name="delete_forum"),
    path("manage-forums/", views.manage_forums, name="manage_forums"),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('guidelines/', views.guidelines, name='guidelines'),  # <- this is required
    path('forums/', views.forum_list, name='forum_list'),  # <-- add this
     path('leaderboard/weekly/', views.weekly_leaderboard, name='weekly_leaderboard'),
    path('leaderboard/daily/', views.daily_leaderboard, name='daily_leaderboard'),  # optional
    path('achievements/', views.achievements, name='achievements'),  # <-- add this
    path('points-system/', views.points_system, name='points_system'),  # <-- add this

    # Existing URLs
    path("forum/<slug:forum_slug>/", views.forum_detail, name="forum_detail"),
    path("discussion/<int:discussion_id>/", views.discussion_detail, name="discussion_detail"),
    path("create/<slug:forum_slug>/", views.create_discussion, name="create_discussion"),
    path("my-discussions/", views.my_discussions, name="my_discussions"),
    path('discussion/<int:pk>/edit/', views.edit_discussion, name='edit_discussion'),
    path('discussion/<int:pk>/delete/', views.delete_discussion, name='delete_discussion'),
    path("search/", views.search_discussions, name="search"),
    path("discussions/", views.all_discussions, name="all_discussions"),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/leaderboard/<str:period>/', views.api_leaderboard, name='api_leaderboard'),
    path('discussion/<int:discussion_id>/add-comment/', views.add_comment, name='add_comment'),
    path("tags/", views.tags_list, name="tags"),
    path('comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]