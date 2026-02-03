import { useEffect, useState } from "react";
import { fetchLeaderboard } from "../api";

function Leaderboard() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchLeaderboard()
      .then(res => setUsers(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="bg-white rounded shadow p-4">
      <h2 className="font-bold mb-3">🔥 Top Users (24h)</h2>

      {users.length === 0 && (
        <p className="text-sm text-gray-500">
          No activity yet.
        </p>
      )}

      {users.map((u, idx) => (
        <div
          key={idx}
          className="flex justify-between text-sm py-1"
        >
          <span>{u.user__username}</span>
          <span className="font-semibold">{u.total_karma}</span>
        </div>
      ))}
    </div>
  );
}

export default Leaderboard;
