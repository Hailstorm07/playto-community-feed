import { useState } from "react";
import { createComment } from "../api";

function Comment({ comment, postId, onCommentAdded }) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyUsername, setReplyUsername] = useState("");
  const [replyContent, setReplyContent] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleReply = async () => {
    if (!replyContent.trim()) return;

    setSubmitting(true);
    try {
      await createComment(postId, replyContent, replyUsername || "Anonymous", comment.id);
      setReplyContent("");
      setReplyUsername("");
      setShowReplyForm(false);
      onCommentAdded?.();
    } catch (error) {
      console.error("Error replying to comment:", error);
    }
    setSubmitting(false);
  };

  return (
    <div className="ml-4 mb-3 border-l-2 border-gray-300 pl-3">
      <p className="text-sm font-semibold text-gray-700">
        {comment.author}
      </p>
      <p className="text-sm text-gray-800">
        {comment.content}
      </p>
      <p className="text-xs text-gray-500 mt-1">
        {new Date(comment.created_at).toLocaleDateString()}
      </p>

      <button
        onClick={() => setShowReplyForm(!showReplyForm)}
        className="text-xs text-blue-600 hover:text-blue-800 mt-2"
      >
        Reply
      </button>

      {showReplyForm && (
        <div className="mt-2 p-2 border rounded bg-gray-50">
          <input
            type="text"
            className="w-full border p-1 rounded mb-1 text-xs"
            placeholder="Your name"
            value={replyUsername}
            onChange={(e) => setReplyUsername(e.target.value)}
          />
          <textarea
            className="w-full border p-1 rounded mb-1 text-xs"
            placeholder="Write a reply..."
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            rows="2"
          />
          <div className="flex gap-1">
            <button
              onClick={handleReply}
              disabled={submitting}
              className="bg-blue-600 text-white px-2 py-1 rounded text-xs hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? "Replying..." : "Reply"}
            </button>
            <button
              onClick={() => setShowReplyForm(false)}
              className="bg-gray-300 px-2 py-1 rounded text-xs hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {comment.replies?.map(reply => (
        <Comment key={reply.id} comment={reply} postId={postId} onCommentAdded={onCommentAdded} />
      ))}
    </div>
  );
}

export default Comment;
