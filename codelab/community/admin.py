from django.contrib import admin
from .models import Forum, Discussion, Comment,Achievement,Tag

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'forum', 'author', 'is_pinned', 'views', 'created_at']
    list_filter = ['forum', 'is_pinned', 'created_at']
    search_fields = ['title', 'content']
    raw_id_fields = ['author']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['discussion', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']
    raw_id_fields = ['author', 'discussion']

admin.site.register(Tag)