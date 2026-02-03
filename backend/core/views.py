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
        try:
            print("REQUEST DATA:", request.data)
            print("REQUEST CONTENT TYPE:", request.content_type)

            user = User.objects.first()
            print(f"USER FOUND: {user}")
            if not user:
                return Response(
                    {"error": "No users exist"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = PostSerializer(data=request.data)
            print(f"SERIALIZER CREATED: {serializer}")

            if serializer.is_valid():
                serializer.save(author=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # 👇 THIS IS CRITICAL
            print("SERIALIZER ERRORS:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"EXCEPTION: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        user = User.objects.first()

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
        user = User.objects.first()
        Comment.objects.create(
            author=user,
            post_id=request.data["post_id"],
            parent_id=request.data.get("parent_id"),
            content=request.data["content"],
        )
        return Response({"status": "ok"})
