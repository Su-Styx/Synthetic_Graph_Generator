import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listRuns } from "../api/runs";

export default function RunsPage() {
  const [runs, setRuns] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRuns() {
      try {
        const data = await listRuns();
        setRuns(data);
        setError("");
        setLoading(false);
      } catch (err) {
        setError(err.message || "Failed to load runs");
        setLoading(false);
      }
    }

    fetchRuns();
  }, []);

  if (loading) return <p>Loading runs...</p>;
  if (error) return <p style={{ color: "crimson" }}>{error}</p>;

  return (
    <div>
      <h2>Runs</h2>
      {runs.length === 0 ? (
        <p>No runs yet.</p>
      ) : (
        <ul>
          {runs.map((run) => (
            <li key={run.id}>
              <Link to={`/runs/${run.id}`}>
                [{run.status}] {run.name} ({run.model})
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}