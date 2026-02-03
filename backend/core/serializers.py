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
    author = serializers.StringRelatedField(read_only=True)
    content = serializers.CharField(allow_blank=True)

    class Meta:
        model = Post
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["author", "created_at"]
