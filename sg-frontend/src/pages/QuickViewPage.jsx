// src/pages/QuickViewPage.jsx
import { useMemo, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { buildGraphData, computeMetrics, extraKeys } from "../utils/graphMetrics";
import bgImage from "../assets/bcg.png";
import "./css/RunDetailPage.css";

const NODE_CORE_KEYS = new Set(["id", "x", "y", "vx", "vy", "index", "fx", "fy"]);
const LINK_CORE_KEYS = new Set(["id", "source", "target", "index"]);

export default function QuickViewPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [showGraph, setShowGraph] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const graphData = useMemo(() => buildGraphData(result), [result]);
  const metrics = useMemo(() => computeMetrics(graphData), [graphData]);
  const nodeKeys = useMemo(() => extraKeys(graphData?.nodes, NODE_CORE_KEYS), [graphData]);
  const linkKeys = useMemo(() => extraKeys(graphData?.links, LINK_CORE_KEYS), [graphData]);

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) {
      setError("Please choose a file to view.");
      return;
    }

    setUploading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file, file.name);

      const res = await fetch("http://localhost:8000/api/quick-view/", {
        method: "POST",
        body: formData,
      });

      const contentType = res.headers.get("content-type") || "";
      const bodyText = await res.text();

      if (!res.ok) {
        throw new Error(`Upload failed (${res.status}): ${bodyText.slice(0, 300)}`);
      }

      if (!contentType.includes("application/json")) {
        throw new Error(`Server returned non-JSON response: ${bodyText.slice(0, 300)}`);
      }

      setResult(JSON.parse(bodyText));
    } catch (err) {
      setError(err.message || "Failed to load graph");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="run-page">
      <div className="run-bg" style={{ backgroundImage: `url(${bgImage})` }} />

      <div className="run-content">
        <header className="run-header">
          <div>
            <span className="run-eyebrow">Quick View</span>
            <h1 className="run-title">Inspect a Graph File</h1>
            <div className="run-tags">
              <span className="tag">no run saved</span>
              <span className="tag">csv / txt / mtx</span>
              {result && <span className="status-tag status-completed">parsed</span>}
            </div>
          </div>

          <form onSubmit={handleUpload} className="run-actions" style={{ gap: "10px", alignItems: "center" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <input
                type="file"
                accept=".csv,.txt,.mtx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <small style={{ color: "rgba(255,255,255,0.65)" }}>
                Supports edge lists (.csv, .txt) and Matrix Market (.mtx)
              </small>
            </div>

            <button className="btn btn-accent" type="submit" disabled={uploading}>
              {uploading ? "Parsing…" : "View Graph"}
            </button>
          </form>
        </header>

        {error && (
          <section className="panel accent">
            <div className="panel-header"><h3 className="panel-title error">Error</h3></div>
            <pre className="code-block error">{error}</pre>
          </section>
        )}

        <div className="run-grid">
          <div className="run-col">
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Graph Visual</h3>
                <Toggle checked={showGraph} onChange={() => setShowGraph((v) => !v)} />
              </div>
              {showGraph ? (
                graphData ? <GraphView data={graphData} /> : <Empty>Upload a file to view its graph.</Empty>
              ) : (
                <Empty>Graph display is hidden. Toggle it back on above.</Empty>
              )}
            </section>

            {(nodeKeys.length > 0 || linkKeys.length > 0) && (
              <section className="panel">
                <div className="panel-header"><h3 className="panel-title">Node &amp; Link Attributes</h3></div>
                <div className="attr-grid">
                  {nodeKeys.length > 0 && <AttrList label="Node attributes" keys={nodeKeys} />}
                  {linkKeys.length > 0 && <AttrList label="Link attributes" keys={linkKeys} />}
                </div>
              </section>
            )}
          </div>

          <div className="run-col">
            <section className="panel">
              <div className="panel-header"><h3 className="panel-title">Graph Metrics</h3></div>
              {metrics ? (
                <div className="metric-list">
                  <Metric label="Nodes" value={metrics.nodeCount} />
                  <Metric label="Edges" value={metrics.edgeCount} />
                  <Metric label="Average degree" value={metrics.avgDegree} />
                  <Metric label="Max degree" value={metrics.maxDegree} />
                  <Metric label="Density" value={metrics.density} />
                  <Metric label="Avg. clustering coefficient" value={metrics.avgClustering} />
                </div>
              ) : (
                <Empty>Metrics will appear once a file is uploaded.</Empty>
              )}
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

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