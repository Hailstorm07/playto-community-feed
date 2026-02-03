import { useEffect, useState } from "react";
import { fetchFeed, createPost } from "../api";

export default function Feed() {
  const [posts, setPosts] = useState([]);
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
    if (!content.trim()) return;

    setLoading(true);
    await createPost(content);
    setContent("");
    setLoading(false);

    loadFeed(); // refresh feed
  };

  return (
    <div className="max-w-xl mx-auto p-4">
      {/* CREATE POST */}
      <div className="mb-6">
        <textarea
          className="w-full border p-2 rounded"
          placeholder="Write a post..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="mt-2 bg-blue-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Posting..." : "Post"}
        </button>
      </div>

      {/* FEED */}
      {posts.map((post) => (
        <div key={post.id} className="border p-3 mb-3 rounded">
          <p>{post.content}</p>
          <div className="text-sm text-gray-500">
            Likes: {post.like_count}
          </div>
        </div>
      ))}
    </div>
  );
}
