
const BASE_URL = "http://127.0.0.1:8000/api";

export async function runWorkloadQuery({ runId, sourceRunId, queryType, queryParams }) {
  const res = await fetch(`${BASE_URL}/workload-query/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      run_id: runId,
      source_run_id: sourceRunId || null,
      query_type: queryType || null,
      query_params: queryParams || {},
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Workload query failed");
  }

  return res.json();
}