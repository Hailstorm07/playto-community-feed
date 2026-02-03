import Feed from "./components/Feed";
import Leaderboard from "./components/Leaderboard";

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow p-4 mb-6">
        <h1 className="text-2xl font-bold text-center">
          Community Feed
        </h1>
      </header>

      <main className="max-w-6xl mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-6">
        <section className="md:col-span-2">
          <Feed />
        </section>

        <aside>
          <Leaderboard />
        </aside>
      </main>
    </div>
  );
}

export default App;
