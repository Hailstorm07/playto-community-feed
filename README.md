# Community Feed

A high-performance **threaded discussion platform** built with Django, DRF, React, and Tailwind CSS. Features nested comments, dynamic karma leaderboards, and optimized database queries.

## ✨ Features

- 📝 **Post & Reply** - Create posts and reply to comments (nested like Reddit)
- 👍 **Gamification** - Earn karma (5 points per post like, 1 point per comment like)
- 🏆 **Live Leaderboard** - Top 5 users from the last 24 hours, updated dynamically
- ⚡ **Optimized** - No N+1 queries, atomic transactions, prevents double-likes

## 🚀 Live Demo

**Frontend:** https://playto-community-feed-production.up.railway.app/  
**Backend API:** https://playto-community-feed-production.up.railway.app/api/

## 🏗️ Tech Stack

- **Backend:** Django 5.0 + Django REST Framework
- **Frontend:** React 18 + Tailwind CSS
- **Database:** SQLite (dev), PostgreSQL (production)
- **Hosting:** Railway

## 🎯 Project Structure

```
playto/
├── backend/
│   ├── core/
│   │   ├── models.py         # Post, Comment, Like, KarmaEvent
│   │   ├── views.py          # API endpoints (FeedView, LikePostView, etc)
│   │   ├── serializers.py    # DRF serializers with prefetch optimization
│   │   ├── urls.py           # URL routing
│   │   └── management/
│   │       └── commands/
│   │           └── create_default_user.py
│   ├── backend/
│   │   ├── settings.py       # CSRF disabled, CORS enabled
│   │   ├── urls.py           # Root URL config
│   │   └── wsgi.py
│   ├── manage.py
│   ├── db.sqlite3            # Database
│   ├── Procfile              # Railway deployment config
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Feed.jsx        # Post creation, feed display
│   │   │   ├── PostCard.jsx    # Post card with like/comment UI
│   │   │   ├── Comment.jsx     # Recursive comment component
│   │   │   └── Leaderboard.jsx # Top 5 users widget
│   │   ├── api.js             # Axios API client
│   │   ├── App.js             # Root component
│   │   └── index.js
│   ├── package.json
│   ├── tailwind.config.js
│   └── public/
│
├── EXPLAINER.md              # Architecture decisions & AI audit
└── README.md                 # This file
```

## 🔧 Local Development

### Prerequisites

- Python 3.13+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create default user (optional)
python manage.py create_default_user

# Start Django server
python manage.py runserver
```

Backend runs on `http://localhost:8000/`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional, defaults to Railway)
echo "REACT_APP_API_BASE=http://localhost:8000/api" > .env.local

# Start React dev server
npm start
```

Frontend runs on `http://localhost:3000/`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/feed/` | Get all posts with comments |
| `POST` | `/api/posts/` | Create a new post |
| `POST` | `/api/like/post/<id>/` | Like/unlike a post |
| `POST` | `/api/comments/` | Create a comment/reply |
| `POST` | `/api/like/comment/<id>/` | Like/unlike a comment |
| `GET` | `/api/leaderboard/` | Get top 5 users (24h) |

**Example: Create Post**

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "content": "Hello world!"}'
```

**Example: Like Post**

```bash
curl -X POST http://localhost:8000/api/like/post/1/ \
  -H "Content-Type: application/json" \
  -d '{"username": "bob"}'
```

## 🏆 Leaderboard Logic

The leaderboard is dynamically calculated from the `KarmaEvent` table:

```python
leaderboard = (
    KarmaEvent.objects
    .filter(created_at__gte=now() - timedelta(hours=24))
    .values("user__username")
    .annotate(total_karma=Sum("points"))
    .order_by("-total_karma")[:5]
)
```

**Karma Rules:**
- Post Like: +5 karma
- Comment Like: +1 karma
- Unlike: removes karma event

## 📚 Architecture Highlights

### No N+1 Queries

Uses `prefetch_related()` with custom `Prefetch` objects to load nested comments efficiently:

```python
Prefetch(
    "comments",
    queryset=Comment.objects
        .filter(parent__isnull=True)    # Only root comments
        .select_related("author")
        .prefetch_related("replies")    # Load all replies at once
)
```

Result: 1 post with 50 nested comments = **3 DB queries**, not 51.

### Race Condition Prevention

Atomic transactions with toggle logic prevent double-likes and karma inflation:

```python
with transaction.atomic():
    like = Like.objects.filter(user=user, post_id=post_id).first()
    if like:
        like.delete()  # Unlike
    else:
        Like.objects.create(...)  # Like
```

### Comment Tree Structure

Uses **adjacency list** pattern with self-referential foreign key:

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", null=True, blank=True, related_name="replies")
    # parent=NULL → root comment
    # parent=<id> → reply to that comment
```

## 🐳 Docker (Optional)

```bash
docker-compose up
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`

## 🧪 Testing

```bash
cd backend

# Run Django tests
python manage.py test core

# Example: Test leaderboard calculation
python manage.py test core.tests.LeaderboardTestCase
```

## 📋 Deployment (Railway)

Both frontend and backend are automatically deployed on git push.

**Backend Procfile:**
```
web: python manage.py migrate && python manage.py create_default_user && gunicorn backend.wsgi
```

**Frontend** uses Railway's built-in Node.js build process.

## 📖 Documentation

See [EXPLAINER.md](EXPLAINER.md) for:
- Database schema & optimization strategies
- Leaderboard query explanation
- AI audit (bugs found & fixed)

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Test locally
4. Push and create a PR

## 📝 License

MIT

---

**Built by:** Aniket Kumar  
**Challenge:** Playto Engineering Interview  
**Date:** February 2026
