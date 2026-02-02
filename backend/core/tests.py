from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from .models import Post, Like
from .models import Comment



from .models import KarmaEvent

class LeaderboardTestCase(TestCase):

    def test_leaderboard_counts_only_last_24_hours(self):
        user = User.objects.create_user(username="alice", password="pass")

        # Karma within last 24h (should count)
        KarmaEvent.objects.create(
            user=user,
            points=5
        )

        # Karma older than 24h (should NOT count)
        old_event = KarmaEvent.objects.create(
            user=user,
            points=100
        )
        KarmaEvent.objects.filter(id=old_event.id).update(
            created_at=now() - timedelta(days=2)
        )

        last_24h = now() - timedelta(hours=24)

        leaderboard = (
            KarmaEvent.objects
            .filter(created_at__gte=last_24h)
            .values("user__username")
            .annotate(total_karma=Sum("points"))
        )

        self.assertEqual(leaderboard[0]["total_karma"], 5)

class LikeConcurrencyTestCase(TestCase):

    def test_user_cannot_like_same_post_twice(self):
        user = User.objects.create_user(username="bob", password="pass")
        post = Post.objects.create(author=user, content="Test post")

        Like.objects.create(user=user, post=post)

        with self.assertRaises(Exception):
            Like.objects.create(user=user, post=post)

class CommentTreeTestCase(TestCase):

    def test_comment_parent_child_relationship(self):
        user = User.objects.create_user(username="charlie", password="pass")
        post = Post.objects.create(author=user, content="Post")

        parent = Comment.objects.create(
            post=post,
            author=user,
            content="Parent comment"
        )

        child = Comment.objects.create(
            post=post,
            author=user,
            parent=parent,
            content="Child comment"
        )

        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())
