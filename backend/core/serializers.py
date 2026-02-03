from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at", "replies"]

    def get_replies(self, obj):
        return CommentSerializer(
            obj.replies.all(), many=True
        ).data
        
        
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    content = serializers.CharField(allow_blank=True)

    class Meta:
        model = Post
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["author", "created_at"]
