import { useEffect, useState } from "react";
import api from "../api";
import PostCard from "./PostCard";

function Feed() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    api.get("feed/")
      .then(res => setPosts(res.data))
      .catch(err => console.error(err));
  }, []);

  if (posts.length === 0) {
    return <p className="text-gray-500">No posts yet.</p>;
  }

  return (
    <>
      {posts.map(post => (
        <PostCard key={post.id} post={post} />
      ))}
    </>
  );
}

export default Feed;
