import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { runWorkloadQuery } from "../api/workload";
import "./css/WorkloadQueryPage.css";

const QUERY_TYPES = [
  { value: "neighbors", label: "Neighbors of node", fields: ["node_id"] },
  { value: "shortest_path", label: "Shortest path", fields: ["source", "target"] },
  { value: "filter_by_attribute", label: "Filter by attribute", fields: ["attribute", "value"] },
  { value: "subgraph_by_type", label: "Subgraph by node type", fields: ["node_type"] },
];

export default function WorkloadQueryPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const runIdFromState = location.state?.runId || "";

  const [runId, setRunId] = useState(runIdFromState);
  const [sourceRunId, setSourceRunId] = useState("");
  const [queryType, setQueryType] = useState("");
  const [queryParams, setQueryParams] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const activeQuery = QUERY_TYPES.find((q) => q.value === queryType);

  async function handleRun() {
    setLoading(true);
    setError("");
    try {
      const data = await runWorkloadQuery({ runId, sourceRunId, queryType, queryParams });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="wq-page">
      <header className="wq-header">
        <div>
          <span className="wq-eyebrow">Evaluation</span>
          <h1 className="wq-title">Workload Query Suite</h1>
          <p className="wq-subtitle">
            Validate structural quality and test queries against generated graph data before export.
          </p>
        </div>
        <button className="btn btn-neutral" onClick={() => navigate(-1)}>← Back to run</button>
      </header>

      <section className="panel">
        <h3 className="panel-title">Run Configuration</h3>
        <div className="wq-form-row">
          <Field label="Run ID">
            <input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="e.g. 42" />
          </Field>
          <Field label="Source/Input Run ID (optional)" hint="For structural fidelity comparison">
            <input value={sourceRunId} onChange={(e) => setSourceRunId(e.target.value)} placeholder="Leave blank if unavailable" />
          </Field>
        </div>
        <button className="btn btn-accent" onClick={handleRun} disabled={!runId || loading}>
          {loading ? "Running…" : "Run Evaluation"}
        </button>
        {error && <p className="wq-error">{error}</p>}
      </section>

      {result && (
        <>
          <MetricsSection title="Preliminary Fields" data={result.metrics.preliminary_fields} />
          <MetricsSection title="Completeness" data={result.metrics.completeness} />
          <MetricsSection title="Structural Similarity" data={result.metrics.structural_fidelity} />
          <MetricsSection title="Quantitative Metrics" data={result.metrics.quantitative_metrics} />

          <section className="panel">
            <h3 className="panel-title">Generic Queries (Baseline Validation)</h3>
            <pre className="code-block">{JSON.stringify(result.generic_queries, null, 2)}</pre>
          </section>

          <section className="panel">
            <h3 className="panel-title">Custom Workload Query</h3>
            <div className="wq-form-row">
              <Field label="Query Type">
                <select value={queryType} onChange={(e) => { setQueryType(e.target.value); setQueryParams({}); }}>
                  <option value="">Select a query…</option>
                  {QUERY_TYPES.map((q) => <option key={q.value} value={q.value}>{q.label}</option>)}
                </select>
              </Field>
              {activeQuery?.fields.map((field) => (
                <Field key={field} label={field}>
                  <input
                    value={queryParams[field] || ""}
                    onChange={(e) => setQueryParams({ ...queryParams, [field]: e.target.value })}
                  />
                </Field>
              ))}
            </div>
            <button className="btn btn-accent" onClick={handleRun} disabled={!queryType}>
              Run Custom Query
            </button>
            {result.custom_query_result && (
              <pre className="code-block">{JSON.stringify(result.custom_query_result, null, 2)}</pre>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function Field({ label, hint, children }) {
  return (
    <div className="wq-field">
      <label>{label}</label>
      {children}
      {hint && <span className="wq-hint">{hint}</span>}
    </div>
  );
}

function MetricsSection({ title, data }) {
  return (
    <section className="panel">
      <h3 className="panel-title">{title}</h3>
      <div className="metric-list">
        {Object.entries(data).map(([key, value]) => (
          <div className="metric-row" key={key}>
            <span>{key.replace(/_/g, " ")}</span>
            <span>{typeof value === "boolean" ? String(value) : String(value)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}