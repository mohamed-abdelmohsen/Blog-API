from rest_framework import serializers
from .models import Category, Tag, Comment, Post, Like ,Bookmark
from django.contrib.auth.models import User

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.IntegerField(source="posts.count", read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'parent', 'body', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'is_active', 'created_at', 'updated_at']

        def get_repplies(self,obj):
            if obj.replies.exists():
                return CommentSerializer(obj.replies.filter(is_active=True), many=True).data
            return []

        
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'parent', 'body']

    def validate_parent(self,value):
        if value and value.parent is not None:
            raise serializers.ValidationError('You cant only add one reply')
        return value
    

class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tag = TagSerializer(read_only=True, many=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source = 'comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "author", "category", "tags",
            "excerpt", "featured_image", "status",
            "created_at", "published_at",
            "views_count", "likes_count", "comments_count",
            "is_liked", "is_bookmarked",
        ]
    def _user(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_is_liked(self,obj):
        user = self._user()
        return bool(user and Like.objects.filter(user=user, post=obj).exists())

    def get_is_bookmarked(self,obj):
        user = self._user()
        return bool(user and Bookmark.objects.filter(user=user, post=obj).exists())


class PostDetailSerializer(PostListSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['content', 'updated_at', 'comments']

    def get_comments(self,obj):
        top_level = obj.comments.filter(parent__isnull=True, is_active=True)
        return CommentSerializer(top_level, many=True, context=self.context).data
    

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(
        child = serializers.CharField(max_length = 50),
        write_only = True,
        required = False
    )
    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "category", "tags", "tag_names",
            "excerpt", "content", "featured_image", "status",
            "published_at",
        ]
        read_only_fields = ["slug", "published_at"]
    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        tags = validated_data.pop("tags", [])

        request = self.context["request"]
        post = Post.objects.create(author=request.user, **validated_data)

        for tag in tags:
            post.tags.add(tag)

        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                slug=name.lower().replace(" ", "-"),
                defaults={"name": name},
            )
            post.tags.add(tag)

        return post

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        tags = validated_data.pop("tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)
        if tag_names is not None:
            tag_objs = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(
                    slug=name.lower().replace(" ", "-"),
                    defaults={"name": name},
                )
                tag_objs.append(tag)
            instance.tags.set(tag_objs)

        return instance


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["user"]


class BookmarkSerializer(serializers.ModelSerializer):
    post = PostListSerializer(read_only=True)

    class Meta:
        model = Bookmark
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["user"]