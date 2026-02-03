from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from django.db.models import Prefetch

from .models import Post, Comment, Like, KarmaEvent
from .serializers import PostSerializer
from .utils import build_comment_tree

class CreatePostView(APIView):
    def post(self, request):
        # Get or create user based on username
        username = request.data.get("username", "Anonymous")
        if not username.strip():
            username = "Anonymous"
        
        user, created = User.objects.get_or_create(username=username)

        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedView(APIView):
    def get(self, request):
        posts = (
            Post.objects
            .select_related("author")
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=Comment.objects.select_related("author").prefetch_related("replies"),
                )
            )
            .order_by("-created_at")
        )

        return Response(PostSerializer(posts, many=True).data)



class LikePostView(APIView):
    def post(self, request, post_id):
        # Get or create user based on username
        username = request.data.get("username", "Anonymous")
        if not username.strip():
            username = "Anonymous"
        
        user, created_user = User.objects.get_or_create(username=username)

        with transaction.atomic():
            like, created = Like.objects.get_or_create(
                user=user,
                post_id=post_id,
            )

            if created:
                KarmaEvent.objects.create(
                    user=Post.objects.get(id=post_id).author,
                    points=5,
                )

        return Response({"liked": created})


class LeaderboardView(APIView):
    def get(self, request):
        since = now() - timedelta(hours=24)

        leaderboard = (
            KarmaEvent.objects
            .filter(created_at__gte=since)
            .values("user__username")
            .annotate(total_karma=Sum("points"))
            .order_by("-total_karma")[:5]
        )

        return Response(leaderboard)

class CreateCommentView(APIView):
    def post(self, request):
        # Get or create user based on username
        username = request.data.get("username", "Anonymous")
        if not username.strip():
            username = "Anonymous"
        
        user, created = User.objects.get_or_create(username=username)
        
        comment = Comment.objects.create(
            author=user,
            post_id=request.data["post_id"],
            parent_id=request.data.get("parent_id"),
            content=request.data["content"],
        )
        return Response({"status": "ok"})
