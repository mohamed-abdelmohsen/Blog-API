from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    CategoryViewSet, TagViewSet, PostViewSet,
    CommentViewSet, MyBookmarksViewSet,
)

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("categories", CategoryViewSet, basename="category")
router.register("tags", TagViewSet, basename="tag")
router.register("comments", CommentViewSet, basename="comment")
router.register("my-bookmarks", MyBookmarksViewSet, basename="my-bookmark")

urlpatterns = [
    path("", include(router.urls)),
]