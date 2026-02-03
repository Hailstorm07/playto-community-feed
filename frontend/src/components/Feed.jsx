import { useEffect, useState } from "react";
import { fetchFeed, createPost } from "../api";
import PostCard from "./PostCard";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [username, setUsername] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  const loadFeed = async () => {
    const res = await fetchFeed();
    setPosts(res.data);
  };

  useEffect(() => {
    loadFeed();
  }, []);

  const handleSubmit = async () => {
    if (!content.trim() || !username.trim()) {
      alert("Please enter both name and post content");
      return;
    }

    setLoading(true);
    try {
      await createPost(username, content);
      setContent("");
      loadFeed(); // refresh feed
    } catch (error) {
      console.error("Error creating post:", error);
    }
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      {/* CREATE POST */}
      <div className="bg-white rounded shadow p-4 mb-6">
        <h2 className="font-bold mb-4">Create a Post</h2>
        <input
          type="text"
          className="w-full border p-2 rounded mb-3"
          placeholder="Your name"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <textarea
          className="w-full border p-2 rounded mb-3"
          placeholder="What's on your mind?"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows="4"
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Posting..." : "Post"}
        </button>
      </div>

      {/* FEED */}
      <div>
        {posts.length === 0 ? (
          <p className="text-center text-gray-500">No posts yet. Be the first!</p>
        ) : (
          posts.map((post) => <PostCard key={post.id} post={post} onPostUpdate={loadFeed} />)
        )}
      </div>
    </div>
  );
}
