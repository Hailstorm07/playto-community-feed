import axios from "axios";

const API_BASE = "https://playto-community-feed-production.up.railway.app/api";

export const fetchFeed = () =>
  axios.get(`${API_BASE}/feed/`);

export const createPost = (username, content) =>
  axios.post(`${API_BASE}/posts/`, { username, content });

export const likePost = (postId, username) =>
  axios.post(`${API_BASE}/like/post/${postId}/`, { username });

export const likeComment = (commentId, username) =>
  axios.post(`${API_BASE}/like/comment/${commentId}/`, { username });

export const createComment = (postId, content, username, parentId = null) =>
  axios.post(`${API_BASE}/comments/`, { post_id: postId, content, username, parent_id: parentId });

export const fetchLeaderboard = () =>
  axios.get(`${API_BASE}/leaderboard/`);
