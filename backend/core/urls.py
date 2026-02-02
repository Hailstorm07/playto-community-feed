from django.urls import path
from .views import FeedView, LikePostView, LeaderboardView

urlpatterns = [
    path("feed/", FeedView.as_view()),
    path("like/post/<int:post_id>/", LikePostView.as_view()),
    path("leaderboard/", LeaderboardView.as_view()),
]
