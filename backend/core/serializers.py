from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at", "children"]

    def get_children(self, obj):
        return CommentSerializer(obj.children_list, many=True).data


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source="author.username",
        read_only=True
    )

    class Meta:
        model = Post
        fields = ["id", "author", "content", "like_count"]
