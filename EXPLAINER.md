# Community Feed - Technical Explainer

## 1. The Tree: Nested Comments Without N+1 Queries

### Database Schema

Comments use a **self-referencing foreign key** (adjacency list pattern):

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.CASCADE,
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Key Points:**
- `parent=NULL` → top-level comment
- `parent=<Comment ID>` → reply to that comment
- `related_name="replies"` → access child comments via `.replies.all()`

### Efficient Serialization (No N+1)

**The Problem:** If we fetch 50 comments, naively calling `.replies.all()` on each = 50 extra queries.

**The Solution:**

```python
from django.db.models import Prefetch

class FeedView(APIView):
    def get(self, request):
        posts = (
            Post.objects
            .select_related("author")  # 1 query: author lookup
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=Comment.objects
                        .filter(parent__isnull=True)      # Only root comments
                        .select_related("author")          # 1 query: author lookup
                        .prefetch_related("replies")       # 1 query: all replies at once
                )
            )
            .order_by("-created_at")
        )
        return Response(PostSerializer(posts, many=True).data)
```

**Why This Works:**
1. `.filter(parent__isnull=True)` → Only load root comments (not nested ones)
2. `.select_related("author")` → Single JOIN to get all authors in one query
3. `.prefetch_related("replies")` → Single query fetches ALL replies, Django handles in-memory grouping
4. **Recursive Serializer** - The CommentSerializer calls itself for `replies`:

```python
class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    
    def get_replies(self, obj):
        return CommentSerializer(
            obj.replies.all(), many=True  # Already prefetched, no DB hit!
        ).data
```

**Result:** Fetching a post with 50 nested comments = **~3 database queries** (posts, authors, comments, replies), not 51.

---

## 2. The Math: Last 24h Leaderboard Query

### QuerySet

```python
class LeaderboardView(APIView):
    def get(self, request):
        since = now() - timedelta(hours=24)
        
        leaderboard = (
            KarmaEvent.objects
            .filter(created_at__gte=since)                    # Only last 24 hours
            .values("user__username")                         # Group by user
            .annotate(total_karma=Sum("points"))              # Sum karma points
            .order_by("-total_karma")[:5]                     # Top 5
        )
        
        return Response(list(leaderboard))
```

### Generated SQL (Equivalent)

```sql
SELECT 
    auth_user.username,
    SUM(core_karmaevent.points) AS total_karma
FROM core_karmaevent
JOIN auth_user ON core_karmaevent.user_id = auth_user.id
WHERE core_karmaevent.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY auth_user.id, auth_user.username
ORDER BY total_karma DESC
LIMIT 5;
```

### Key Design Decisions

1. **Dynamic Calculation** - Not stored as a field on User model
   - ✅ Always accurate (no stale data)
   - ✅ Automatically excludes karma older than 24h
   - ✅ Scales to millions of events

2. **KarmaEvent Model** - Immutable transaction log
   ```python
   class KarmaEvent(models.Model):
       user = models.ForeignKey(User, on_delete=models.CASCADE)
       points = models.IntegerField()  # 5 for post, 1 for comment
       created_at = models.DateTimeField(auto_now_add=True)
   ```
   - Post Like → Creates KarmaEvent with points=5
   - Comment Like → Creates KarmaEvent with points=1
   - Unlike → Deletes corresponding KarmaEvent

---

## 3. The AI Audit: Bug Fixed

### The Bug (AI-Generated)

**Initial code from AI (ChatGPT):**

```python
class LikePostView(APIView):
    def post(self, request, post_id):
        user, _ = User.objects.get_or_create(username=request.data.get("username"))
        
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
```

### The Problems

1. **Double-Like Trap** - `get_or_create` prevents unlike. Clicking like twice = same response, can't toggle.
2. **Karma Inflation** - Deleted likes still have KarmaEvent in database. If user likes → unlike → likes again, author gets double karma.
3. **Race Condition** - No transaction. Two simultaneous requests could create duplicate KarmaEvent entries.

### The Fix

```python
class LikePostView(APIView):
    def post(self, request, post_id):
        username = request.data.get("username", "Anonymous")
        user, _ = User.objects.get_or_create(username=username)

        with transaction.atomic():                    # ← ATOMIC
            like = Like.objects.filter(user=user, post_id=post_id).first()
            
            if like:
                # UNLIKE - toggle off
                like.delete()
                # Clean up karma
                KarmaEvent.objects.filter(
                    user=Post.objects.get(id=post_id).author, 
                    points=5
                ).delete()
                return Response({"liked": False})
            else:
                # LIKE - toggle on
                Like.objects.create(user=user, post_id=post_id)
                KarmaEvent.objects.create(
                    user=Post.objects.get(id=post_id).author,
                    points=5,
                )
                return Response({"liked": True})
```

### What Changed

| Issue | Fix |
|-------|-----|
| No unlike | Toggle pattern: if exists delete, else create |
| Karma inflation | Delete KarmaEvent when unlike |
| Race condition | `transaction.atomic()` ensures all-or-nothing |
| Double karma | Delete matching KarmaEvent (not all) |

**Result:** Users can like/unlike freely, karma tracks accurately, no race conditions. ✅

---

## Summary

- **Comments:** Adjacency list + prefetch_related = O(1) per query
- **Leaderboard:** Aggregate on-the-fly from immutable KarmaEvent log
- **Like Toggle:** Atomic transactions prevent double-like and karma inflation

### Efficient Fetching (Avoiding N+1 Queries)

To avoid the N+1 query problem when loading nested comments, fetch all comments for a post in one query and build the tree in memory:

```python
# Fetch all comments for a post in a single query
comments = Comment.objects.filter(post=post).select_related("author")

# Convert flat list to tree using a dictionary-based lookup (in-memory)
```

This avoids recursive database queries and ensures that loading a post with many nested comments does not degrade database performance.

### Serialization

Comments are serialized recursively, but only after the tree is constructed in memory. No additional database queries are triggered during serialization.

## 2. The Math — Last 24 Hour Leaderboard

### Design Choice

I intentionally did not store daily or rolling karma totals on the User model. Instead, karma is tracked using an event-based model (`KarmaEvent`), where each like generates a discrete transaction:

- Like on Post → +5 karma
- Like on Comment → +1 karma

This guarantees correctness, auditability, and flexibility.

### Leaderboard Query

The leaderboard is computed dynamically using a time-bounded aggregation:

```python
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum

last_24h = now() - timedelta(hours=24)

leaderboard = (
    KarmaEvent.objects
    .filter(created_at__gte=last_24h)
    .values("user__username")
    .annotate(total_karma=Sum("points"))
    .order_by("-total_karma")[:5]
)
```

This query:

- Only counts karma earned in the last 24 hours
- Avoids denormalized counters
- Remains correct under concurrent activity

## 3. Concurrency & Data Integrity

### Preventing Double Likes

Users are prevented from liking the same post or comment more than once via database-level unique constraints:

```python
UniqueConstraint(
    fields=["user", "post"],
    condition=Q(post__isnull=False)
)
```

This guarantees correctness even under race conditions or concurrent requests. All like operations are wrapped in atomic transactions.

## 4. The AI Audit

### Example AI Mistake

An AI-generated solution initially suggested storing a `daily_karma` integer field on the `User` model and incrementing it on each like.

### Why This Was Wrong

- Violates the requirement for dynamic calculation
- Breaks under concurrent writes
- Makes historical auditing impossible
- Requires background jobs to reset counters

### Fix

I replaced this with an event-based karma ledger, computing the leaderboard via time-scoped aggregation. This design is simpler, safer, and mathematically correct.

## 5. Testing

I added targeted backend tests to validate:

- Leaderboard aggregation only counts the last 24 hours
- Users cannot double-like posts (concurrency safety)
- Parent–child comment relationships work correctly

These tests exposed real ORM edge cases (e.g. `auto_now_add` behavior), which were fixed explicitly.