function Comment({ comment }) {
  return (
    <div className="ml-4 mt-2 border-l pl-3">
      <p className="text-sm font-semibold">
        {comment.author}
      </p>
      <p className="text-sm">
        {comment.content}
      </p>

      {comment.children.map(child => (
        <Comment key={child.id} comment={child} />
      ))}
    </div>
  );
}

export default Comment;
