function Comment({ comment }) {
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

      {comment.replies?.map(reply => (
        <Comment key={reply.id} comment={reply} />
      ))}
    </div>
  );
}

export default Comment;
