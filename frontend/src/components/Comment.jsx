import { useState } from "react";
import { createComment, likeComment } from "../api";

function Comment({ comment, postId, onCommentAdded }) {
  const [commentData, setCommentData] = useState(comment);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyUsername, setReplyUsername] = useState("");
  const [replyContent, setReplyContent] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [liking, setLiking] = useState(false);

  const handleLike = async () => {
    setLiking(true);
    try {
      const res = await likeComment(commentData.id, replyUsername || "Anonymous");
      if (res.data.liked) {
        setCommentData({ ...commentData, like_count: (commentData.like_count || 0) + 1 });
      } else {
        setCommentData({ ...commentData, like_count: Math.max(0, (commentData.like_count || 0) - 1) });
      }
    } catch (error) {
      console.error("Error liking comment:", error);
    }
    setLiking(false);
  };

  const handleReply = async () => {
    if (!replyContent.trim()) return;

    setSubmitting(true);
    try {
      const res = await createComment(postId, replyContent, replyUsername || "Anonymous", commentData.id);
      
      // Add reply to local state instead of refreshing
      const newReply = {
        id: Math.random(),
        author: replyUsername || "Anonymous",
        content: replyContent,
        created_at: new Date().toISOString(),
        replies: [],
        like_count: 0
      };
      setCommentData({
        ...commentData,
        replies: [...(commentData.replies || []), newReply]
      });
      
      setReplyContent("");
      setReplyUsername("");
      setShowReplyForm(false);
    } catch (error) {
      console.error("Error replying to comment:", error);
    }
    setSubmitting(false);
  };

  return (
    <div className="ml-4 mb-3 border-l-2 border-gray-300 pl-3">
      <p className="text-sm font-semibold text-gray-700">
        {commentData.author}
      </p>
      <p className="text-sm text-gray-800">
        {commentData.content}
      </p>
      <p className="text-xs text-gray-500 mt-1">
        {new Date(commentData.created_at).toLocaleDateString()}
      </p>

      <button
        onClick={() => setShowReplyForm(!showReplyForm)}
        className="text-xs text-blue-600 hover:text-blue-800 mt-2 mr-3"
      >
        Reply
      </button>
      <button
        onClick={handleLike}
        disabled={liking}
        className="text-xs text-blue-600 hover:text-blue-800 mt-2 disabled:opacity-50"
      >
        👍 {commentData.like_count || 0}
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
