from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum

from .models import Post, Comment, Like, KarmaEvent
from .serializers import PostSerializer
from .utils import build_comment_tree

class CreatePostView(APIView):
    def post(self, request):
        user = User.objects.first()

        if not user:
            return Response(
                {"error": "No users exist"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PostSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedView(APIView):
    def get(self, request):
        posts = Post.objects.all().select_related("author")

        for post in posts:
            comments = Comment.objects.filter(post=post).select_related("author")
            post.comment_tree = build_comment_tree(comments)

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class LikePostView(APIView):
    @transaction.atomic
    def post(self, request, post_id):
        post = Post.objects.select_for_update().get(id=post_id)

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post
        )

        if not created:
            return Response({"detail": "Already liked"}, status=400)

        KarmaEvent.objects.create(user=post.author, points=5)
        return Response({"status": "liked"})


class LeaderboardView(APIView):
    def get(self, request):
        last_24h = now() - timedelta(hours=24)

        data = (
            KarmaEvent.objects
            .filter(created_at__gte=last_24h)
            .values("user__username")
            .annotate(total_karma=Sum("points"))
            .order_by("-total_karma")[:5]
        )

        return Response(data)
