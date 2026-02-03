import { useState } from "react";
import { likePost, createComment } from "../api";
import Comment from "./Comment";

function PostCard({ post, onPostUpdate }) {
  const [showCommentForm, setShowCommentForm] = useState(false);
  const [commentUsername, setCommentUsername] = useState("");
  const [commentContent, setCommentContent] = useState("");
  const [liking, setLiking] = useState(false);

  const handleLike = async () => {
    setLiking(true);
    try {
      await likePost(post.id, commentUsername || "Anonymous");
      onPostUpdate?.();
    } catch (error) {
      console.error("Error liking post:", error);
    }
    setLiking(false);
  };

  const handleAddComment = async () => {
    if (!commentContent.trim()) return;

    try {
      await createComment(post.id, commentContent, commentUsername || "Anonymous");
      setCommentContent("");
      setCommentUsername("");
      setShowCommentForm(false);
      onPostUpdate?.();
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  };

  return (
    <div className="bg-white rounded shadow p-4 mb-6">
      <div className="mb-2 flex justify-between items-center">
        <span className="font-semibold">{post.author}</span>
        <span className="text-sm text-gray-500">{new Date(post.created_at).toLocaleDateString()}</span>
      </div>

      <p className="mb-4 text-gray-800">{post.content}</p>

      {/* LIKE BUTTON */}
      <div className="mb-4 flex gap-4">
        <button
          onClick={handleLike}
          disabled={liking}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-800 disabled:opacity-50"
        >
          👍 {post.like_count} Likes
        </button>
        <button
          onClick={() => setShowCommentForm(!showCommentForm)}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
        >
          💬 Comment
        </button>
      </div>

      {/* COMMENT FORM */}
      {showCommentForm && (
        <div className="mb-4 p-3 border rounded bg-gray-50">
          <input
            type="text"
            className="w-full border p-2 rounded mb-2 text-sm"
            placeholder="Your name"
            value={commentUsername}
            onChange={(e) => setCommentUsername(e.target.value)}
          />
          <textarea
            className="w-full border p-2 rounded mb-2 text-sm"
            placeholder="Write a comment..."
            value={commentContent}
            onChange={(e) => setCommentContent(e.target.value)}
            rows="2"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddComment}
              className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
            >
              Post Comment
            </button>
            <button
              onClick={() => setShowCommentForm(false)}
              className="bg-gray-300 px-3 py-1 rounded text-sm hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* COMMENTS */}
      <div className="border-t pt-4">
        <h3 className="font-semibold text-sm mb-3">
          Comments ({post.comments?.length || 0})
        </h3>

        {post.comments?.length === 0 && (
          <p className="text-sm text-gray-500">No comments yet.</p>
        )}

        {post.comments?.map((c) => (
          <Comment key={c.id} comment={c} postId={post.id} onCommentAdded={onPostUpdate} />
        ))}
      </div>
    </div>
  );
}

export default PostCard;
