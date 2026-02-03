import axios from "axios";

const API_BASE = "https://playto-community-feed-production.up.railway.app/api";

export const fetchFeed = () =>
  axios.get(`${API_BASE}/feed/`);

export const createPost = (content) =>
  axios.post(`${API_BASE}/posts/`);

export const fetchLeaderboard = () =>
  axios.get(`${API_BASE}/leaderboard/`);
