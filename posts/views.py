from django.contrib.admin import action
from django.shortcuts import render
from .models import Category, Tag, Post, Comment, Like, Bookmark
from .serilizers import CategorySerializer, TagSerializer, PostListSerializer\
    , CommentSerializer, CommentCreateSerializer, PostDetailSerializer, PostCreateUpdateSerializer\
    , BookmarkSerializer
from rest_framework import viewsets ,status, permissions, filters
from .permissions import IsAuthorOrReadOnly, IsCommentOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F, Q
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags', 'likes', 'comments')
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "excerpt", "content"]
    ordering_fields = ['published_at', 'created_at', 'views_count', 'likes_count', 'comments_count']
    ordering = ['-published_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user   

        if not user.is_authenticated:
            return qs.filter(status=Post.Status.PUBLISHED)
        return qs.filter(Q(status=Post.Status.PUBLISHED) | Q(author=user))

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
    
        if self.action == 'retrieve':
            return PostDetailSerializer
        
        return PostCreateUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(views_count=F('views_count')+1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'detail':'Post unliked.'}, status=status.http_200_OK)
        return Response({'detail':'Liked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def bookmark(self, request, slug=None):
        post = self.get_object()
        bm, created = Bookmark.objects.get_or_create(user=request.user, post=post)
        if not created:
            bm.delete()
            return Response({'detail':'Bookmark removed'}, status=status.HTTP_200_OK)
        return Response({'detail':'Bookmarked'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def publish(self, request, slug=None):
        post = self.get_object()
        if post.author != request.user:
            return Response({'detail':'Not your post, Not Allowed'}, status=status.HTTP_403_FORBIDDEN)
        post.status = Post.Status.PUBLISHED
        post.save()
        return Response({'detail':'Published'}, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('post', 'author', 'parent').prefetch_related('replies')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post__slug']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class MyBookmarksViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related("post")