# Playto Engineering Challenge – Explainer

This document explains the core architectural and technical decisions behind the Community Feed prototype.

---

## 1. The Tree — Nested Comments

### Data Modeling

I modeled threaded comments using an **adjacency list** approach.

Each `Comment` has an optional `parent` field that is a self-referential foreign key:

```python
parent = models.ForeignKey(
    "self",
    null=True,
    blank=True,
    related_name="children",
    on_delete=models.CASCADE
)
This approach keeps the schema simple while still supporting arbitrarily deep nesting (similar to Reddit).

# Playto Engineering Challenge – Explainer

This document explains the core architectural and technical decisions behind the Community Feed prototype.

---

## 1. The Tree — Nested Comments

### Data Modeling

I modeled threaded comments using an **adjacency list** approach.

Each `Comment` has an optional `parent` field that is a self-referential foreign key:

```python
parent = models.ForeignKey(
    "self",
    null=True,
    blank=True,
    related_name="children",
    on_delete=models.CASCADE,
)
```

This approach keeps the schema simple while still supporting arbitrarily deep nesting (similar to Reddit).

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