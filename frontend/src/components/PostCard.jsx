import Comment from "./Comment";

function PostCard({ post }) {
  return (
    <div className="bg-white rounded shadow p-4 mb-6">
      <div className="mb-2">
        <span className="font-semibold">{post.author}</span>
      </div>

      <p className="mb-4">{post.content}</p>

      <div>
        <h3 className="font-semibold text-sm mb-2">
          Comments
        </h3>

        {post.comments.length === 0 && (
          <p className="text-sm text-gray-500">
            No comments yet.
          </p>
        )}

        {post.comments.map(c => (
          <Comment key={c.id} comment={c} />
        ))}
      </div>
    </div>
  );
}

export default PostCard;
