from django.contrib import admin
from .models import Career, BlogPost, BlogCategory, BlogComment

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "job_type", "is_active", "created_at")
    list_filter = ("job_type", "is_active")
    search_fields = ("title", "location", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("title",)
    prepopulated_fields = {"slug": ("title",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published", "created_at")
    list_filter = ("published", "category")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "name", "created_at")
    search_fields = ("name", "comment")
    list_filter = ("created_at",)
