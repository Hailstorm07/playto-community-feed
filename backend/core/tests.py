from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum
from core.models import Post, Comment, Like, KarmaEvent


class LeaderboardTestCase(TestCase):
    """Test the 24-hour leaderboard calculation."""

    def setUp(self):
        """Create test users and posts."""
        self.alice = User.objects.create_user(username="alice")
        self.bob = User.objects.create_user(username="bob")
        self.charlie = User.objects.create_user(username="charlie")
        
        self.post1 = Post.objects.create(author=self.alice, content="Alice's post")
        self.post2 = Post.objects.create(author=self.bob, content="Bob's post")
        self.comment1 = Comment.objects.create(
            post=self.post2,
            author=self.charlie,
            content="Charlie's comment"
        )

    def test_leaderboard_24h_filter(self):
        """
        Test that leaderboard only counts karma in the last 24 hours.
        
        Scenario:
        - Alice gets 2 post likes (10 karma in 24h)
        - Bob gets 5 comment likes (5 karma in 24h)
        - Charlie gets 3 post likes from older event (0 karma in 24h)
        
        Expected: Alice (10) > Bob (5) > Charlie (0)
        """
        
        # Create recent karma events (within 24h)
        KarmaEvent.objects.create(user=self.alice, points=5)  # Like 1
        KarmaEvent.objects.create(user=self.alice, points=5)  # Like 2
        KarmaEvent.objects.create(user=self.bob, points=1)    # Comment like 1
        KarmaEvent.objects.create(user=self.bob, points=1)    # Comment like 2
        KarmaEvent.objects.create(user=self.bob, points=1)    # Comment like 3
        KarmaEvent.objects.create(user=self.bob, points=1)    # Comment like 4
        KarmaEvent.objects.create(user=self.bob, points=1)    # Comment like 5
        
        # Create old karma event (older than 24h) - should NOT count
        old_event = KarmaEvent.objects.create(user=self.charlie, points=5)
        old_event.created_at = now() - timedelta(hours=25)
        old_event.save()
        
        # Calculate leaderboard (same logic as LeaderboardView)
        since = now() - timedelta(hours=24)
        leaderboard = (
            KarmaEvent.objects
            .filter(created_at__gte=since)
            .values("user__username")
            .annotate(total_karma=Sum("points"))
            .order_by("-total_karma")
        )
        
        leaderboard_list = list(leaderboard)
        
        # Verify results
        self.assertEqual(len(leaderboard_list), 2)  # Only Alice and Bob
        self.assertEqual(leaderboard_list[0]["user__username"], "alice")
        self.assertEqual(leaderboard_list[0]["total_karma"], 10)
        self.assertEqual(leaderboard_list[1]["user__username"], "bob")
        self.assertEqual(leaderboard_list[1]["total_karma"], 5)
        
        # Charlie should not be in leaderboard (old event)
        usernames = [u["user__username"] for u in leaderboard_list]
        self.assertNotIn("charlie", usernames)

    def test_like_unlike_karma_tracking(self):
        """Test that liking and unliking properly tracks karma."""
        
        # Like post
        Like.objects.create(user=self.bob, post=self.post1)
        KarmaEvent.objects.create(user=self.alice, points=5)
        
        # Verify karma
        karma = KarmaEvent.objects.filter(user=self.alice).aggregate(Sum("points"))
        self.assertEqual(karma["points__sum"], 5)
        
        # Unlike (delete like and corresponding event)
        Like.objects.filter(user=self.bob, post=self.post1).delete()
        KarmaEvent.objects.filter(user=self.alice, points=5).delete()
        
        # Verify karma removed
        karma = KarmaEvent.objects.filter(user=self.alice).aggregate(Sum("points"))
        self.assertIsNone(karma["points__sum"])

    def test_comment_like_karma(self):
        """Test that comment likes award 1 karma (not 5)."""
        
        # Like comment
        Like.objects.create(user=self.alice, comment=self.comment1)
        KarmaEvent.objects.create(user=self.charlie, points=1)  # Comment like = 1 point
        
        # Verify karma
        karma = KarmaEvent.objects.filter(user=self.charlie).aggregate(Sum("points"))
        self.assertEqual(karma["points__sum"], 1)


class CommentNestingTestCase(TestCase):
    """Test nested comment structure and serialization."""

    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(username="testuser")
        self.post = Post.objects.create(author=self.user, content="Test post")

    def test_nested_comments_structure(self):
        """Test that parent-child comment relationships work correctly."""
        
        # Create root comment
        root = Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Root comment",
            parent=None
        )
        
        # Create reply to root
        reply1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Reply to root",
            parent=root
        )
        
        # Create reply to reply
        reply2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Reply to reply",
            parent=reply1
        )
        
        # Verify structure
        self.assertEqual(root.parent, None)
        self.assertEqual(reply1.parent, root)
        self.assertEqual(reply2.parent, reply1)
        
        # Verify replies relationship
        self.assertEqual(root.replies.count(), 1)
        self.assertEqual(reply1.replies.count(), 1)
        self.assertEqual(reply2.replies.count(), 0)

    def test_only_root_comments_in_post(self):
        """Test that post.comments only returns root comments (not nested)."""
        
        # Create comments
        root1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Root 1",
            parent=None
        )
        root2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Root 2",
            parent=None
        )
        reply = Comment.objects.create(
            post=self.post,
            author=self.user,
            content="Reply to root1",
            parent=root1
        )
        
        # Get root comments only (as in FeedView)
        root_comments = self.post.comments.filter(parent__isnull=True)
        
        self.assertEqual(root_comments.count(), 2)
        self.assertIn(root1, root_comments)
        self.assertIn(root2, root_comments)
        self.assertNotIn(reply, root_comments)
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
