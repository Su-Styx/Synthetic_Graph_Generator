import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ForceGraph2D from "react-force-graph-2d";
import { getRun } from "../api/runs";
import { buildGraphData, computeMetrics, extraKeys } from "../utils/graphMetrics";
import bgImage from "../assets/bcg.png";
import "./css/RunDetailPage.css";

const NODE_CORE_KEYS = new Set(["id", "x", "y", "vx", "vy", "index", "fx", "fy"]);
const LINK_CORE_KEYS = new Set(["id", "source", "target", "index"]);
const FORMATS = ["CSV", "Neo4j", "RDF", "JSON"];
const MAX_DISPLAY_NODES = 1500;

export default function RunDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [run, setRun] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showGraph, setShowGraph] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    let intervalId;
    async function fetchRun() {
      try {
        const data = await getRun(id); // make sure this returns `result`
        setRun(data);
        setError("");
        setLoading(false);
        if (!["pending", "running"].includes(data.status)) clearInterval(intervalId);
      } catch (err) {
        setError(err.message || "Failed to load run");
        setLoading(false);
      }
    }
    fetchRun();
    intervalId = setInterval(fetchRun, 2500);
    return () => clearInterval(intervalId);
  }, [id]);

  const graphData = useMemo(() => {
    const result = run?.result;
    if (!result) return null;

    const nNodes =
      result.metadata?.n_nodes ??
      (Array.isArray(result.nodes) ? result.nodes.length : 0);

    if (nNodes > MAX_DISPLAY_NODES) {
      return null;
    }

    return buildGraphData(result);
  }, [run]);

  const metrics = useMemo(() => {
    if (!graphData) return null;
    return computeMetrics(graphData);
  }, [graphData]);

  const nodeKeys = useMemo(
    () => extraKeys(graphData?.nodes, NODE_CORE_KEYS),
    [graphData]
  );
  const linkKeys = useMemo(
    () => extraKeys(graphData?.links, LINK_CORE_KEYS),
    [graphData]
  );

  if (loading) return <Centered>Loading run…</Centered>;
  if (error) return <Centered color="#ff8b8b">{error}</Centered>;
  if (!run) return <Centered>No run found.</Centered>;

  return (
    <div className="run-page">
      <div className="run-bg" style={{ backgroundImage: `url(${bgImage})` }} />

      <div className="run-content">
        <header className="run-header">
          <div>
            <span className="run-eyebrow">Run Detail</span>
            <h1 className="run-title">{run.name || "Untitled Run"}</h1>
            <div className="run-tags">
              <span className="tag">{run.job_type}</span>
              <span className="tag">{run.model}</span>
              <span className={`status-tag status-${run.status}`}>{run.status}</span>
            </div>
          </div>
          <div className="run-actions">
            <button className="btn btn-neutral" onClick={() => setShowModal(true)}>
              ⬇ Download
            </button>
            <button
              className="btn btn-accent"
              onClick={() => navigate("/workload-query", { state: { runId: run.id } })}
            >
              Workload Query Suite
            </button>
          </div>
        </header>

        <div className="run-grid">
          <div className="run-col">
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Graph Visual</h3>
                <Toggle checked={showGraph} onChange={() => setShowGraph((v) => !v)} />
              </div>
              {showGraph ? (
                graphData ? (
                  <GraphView data={graphData} />
                ) : run?.result ? (
                  <Empty>
                    Graph is too large to display interactively in the browser
                    (over {MAX_DISPLAY_NODES} nodes). Use the download options to inspect it.
                  </Empty>
                ) : (
                  <Empty>No graph visual available for this run result.</Empty>
                )
              ) : (
                <Empty>Graph display is hidden. Toggle it back on above.</Empty>
              )}
            </section>

            {(nodeKeys.length > 0 || linkKeys.length > 0) && (
              <section className="panel">
                <div className="panel-header">
                  <h3 className="panel-title">Node &amp; Link Attributes</h3>
                </div>
                <div className="attr-grid">
                  {nodeKeys.length > 0 && (
                    <AttrList label="Node attributes" keys={nodeKeys} />
                  )}
                  {linkKeys.length > 0 && (
                    <AttrList label="Link attributes" keys={linkKeys} />
                  )}
                </div>
              </section>
            )}

            {run.error_message && (
              <section className="panel accent">
                <div className="panel-header">
                  <h3 className="panel-title error">Error</h3>
                </div>
                <pre className="code-block error">{run.error_message}</pre>
              </section>
            )}
          </div>

          <div className="run-col">
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Graph Metrics</h3>
              </div>
              {metrics ? (
                <div className="metric-list">
                  <Metric label="Nodes" value={metrics.nodeCount} />
                  <Metric label="Edges" value={metrics.edgeCount} />
                  <Metric label="Average degree" value={metrics.avgDegree} />
                  <Metric label="Max degree" value={metrics.maxDegree} />
                  <Metric label="Density" value={metrics.density} />
                  <Metric
                    label="Avg. clustering coefficient"
                    value={metrics.avgClustering}
                  />
                </div>
              ) : (
                <Empty>Metrics unavailable until the graph is computed.</Empty>
              )}
            </section>

            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Parameters</h3>
              </div>
              <pre className="code-block params">
                {JSON.stringify(run.params ?? {}, null, 2)}
              </pre>
            </section>
          </div>
        </div>
      </div>

      {showModal && <DownloadModal onClose={() => setShowModal(false)} />}
    </div>
  );
}

const Centered = ({ children, color = "#f4f4f4" }) => (
  <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#111", color }}>
    {children}
  </div>
);

const Empty = ({ children }) => <p className="empty-note">{children}</p>;

const Metric = ({ label, value }) => (
  <div className="metric-row"><span>{label}</span><span>{value}</span></div>
);

const AttrList = ({ label, keys }) => (
  <div>
    <p className="attr-label">{label}</p>
    <div className="tag-row">{keys.map((k) => <span key={k} className="tag">{k}</span>)}</div>
  </div>
);

const Toggle = ({ checked, onChange }) => (
  <button type="button" className="toggle" onClick={onChange}>
    {checked ? "Visible" : "Hidden"}
    <span className={`toggle-track ${checked ? "on" : ""}`}>
      <span className={`toggle-thumb ${checked ? "on" : ""}`} />
    </span>
  </button>
);

function GraphView({ data }) {
  return (
    <div className="graph-box">
      <ForceGraph2D
        graphData={data}
        nodeLabel={(n) => n.name || n.label || n.id}
        linkLabel={(l) => l.label || `${l.source} → ${l.target}`}
        nodeCanvasObject={(node, ctx, scale) => {
          const label = node.name || node.label || node.id;
          ctx.font = `${12 / scale}px Arial`;
          ctx.fillStyle = "#c0524b";
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
          ctx.fill();
          ctx.fillStyle = "#f4f4f4";
          ctx.fillText(label, node.x + 8, node.y + 4);
        }}
        linkColor={() => "rgba(255,255,255,0.35)"}
        linkWidth={1.1}
        backgroundColor="#111417"
        cooldownTicks={100}
      />
    </div>
  );
}

function DownloadModal({ onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 style={{ margin: 0, color: "#fff", fontSize: "1.1rem" }}>Download Graph</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="format-grid">
          {FORMATS.map((f) => <button key={f} className="format-btn">{f}</button>)}
        </div>
      </div>
    </div>
  );
}