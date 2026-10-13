from django.contrib import admin
from django.contrib import admin
from .models import Category, Tag, Post, Comment, Like, Bookmark


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class CommentInline(admin.TabularInline):
    """Allows viewing and editing comments directly from inside a Post page."""
    model = Comment
    extra = 0
    fields = ["author", "body", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "category",
        "status",
        "published_at",
        "created_at",
    ]
    list_filter = ["status", "category", "tags", "created_at", "published_at"]
    search_fields = ["title", "body", "author__username"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]  # Speeds up admin loading when having many users
    autocomplete_fields = ["category", "tags"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    inlines = [CommentInline]

    actions = ["make_published", "make_draft"]

    @admin.action(description="Mark selected posts as Published")
    def make_published(self, request, queryset):
        queryset.update(status=Post.Status.PUBLISHED)

    @admin.action(description="Mark selected posts as Draft")
    def make_draft(self, request, queryset):
        queryset.update(status=Post.Status.DRAFT)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "author__username", "post__title"]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title']