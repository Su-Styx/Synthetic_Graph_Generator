import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getRun } from "../api/runs";

export default function RunDetailPage() {
  const { id } = useParams();
  const [run, setRun] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let intervalId;

    async function fetchRun() {
      try {
        const data = await getRun(id);
        setRun(data);
        setError("");
        setLoading(false);

        if (data.status !== "pending" && data.status !== "running" && intervalId) {
          clearInterval(intervalId);
        }
      } catch (err) {
        setError(err.message || "Failed to load run");
        setLoading(false);
      }
    }

    fetchRun();
    intervalId = setInterval(fetchRun, 2500);

    return () => clearInterval(intervalId);
  }, [id]);

  if (loading) return <p>Loading run...</p>;
  if (error) return <p style={{ color: "crimson" }}>{error}</p>;
  if (!run) return <p>No run found.</p>;

  return (
    <div>
      <h2>Run Detail</h2>
      <p><strong>ID:</strong> {run.id}</p>
      <p><strong>Name:</strong> {run.name}</p>
      <p><strong>Job Type:</strong> {run.job_type}</p>
      <p><strong>Model:</strong> {run.model}</p>
      <p><strong>Status:</strong> {run.status}</p>

      <h3>Params</h3>
      <pre>{JSON.stringify(run.params, null, 2)}</pre>

      <h3>Result</h3>
      <pre>{JSON.stringify(run.result, null, 2)}</pre>

      {run.error_message ? (
        <>
          <h3>Error</h3>
          <pre>{run.error_message}</pre>
        </>
      ) : null}
    </div>
  );
}