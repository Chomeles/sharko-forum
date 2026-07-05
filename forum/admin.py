from django.contrib import admin

from .models import Category, Post, Thread


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "position")
    list_editable = ("position",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "created", "is_pinned", "is_locked")
    list_editable = ("is_pinned", "is_locked")
    list_filter = ("category", "is_pinned", "is_locked")
    search_fields = ("title", "author__username")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("__str__", "thread", "author", "created")
    list_filter = ("created",)
    search_fields = ("body", "author__username")
