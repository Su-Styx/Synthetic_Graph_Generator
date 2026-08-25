import { useEffect, useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authFetch } from "../api/authFetch";
import { Panel } from "./ui/Panel-Light";
import { Button } from "./ui/Button";
import { Field } from "./ui/Field";
import { Modal } from "./ui/Modal";
import bgImage from "../assets/bcg.png";
import "./css/tokens.css";
import "./css/ui.css";
import "./css/ModelListPage.css";

export default function ModelListPage() {
  const navigate = useNavigate();

  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchInput, setSearchInput] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState(""); // "" | "type" | "efficiency"
  const [invert, setInvert] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);

  const fetchModels = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.set("search", searchTerm);
      if (sortBy) params.set("sort_by", sortBy);
      params.set("invert", invert ? "true" : "false");

      const res = await authFetch(`http://127.0.0.1:8000/api/models/?${params}`);
      if (!res.ok) throw new Error("Failed to load models");

      const data = await res.json();
      setModels(Array.isArray(data) ? data : []);
    } catch {
      setError("Could not load models");
    } finally {
      setLoading(false);
    }
  }, [searchTerm, sortBy, invert]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  return (
    <div className="model-page">
      <div className="model-bg" style={{ backgroundImage: `url(${bgImage})` }} />

      <div className="model-content">
        <Link to="/settings" className="model-avatar-link">
          👤
        </Link>

        <div className="model-header">
          <div>
            <div className="model-eyebrow">Graph Generation Workspace</div>
            <h1 className="model-title">Models</h1>
          </div>
        </div>

        <div className="model-grid">
          <div className="model-sidebar">
            <Panel title="Dashboard" action={<span className="tag">Back</span>}>
              <p className="model-sidebar-text">
                Return to your dashboard to see current and past graph generation runs.
              </p>
              <Button variant="neutral" onClick={() => navigate("/dashboard")} style={{ width: "100%" }}>
                Back to Dashboard
              </Button>
            </Panel>

            <Panel title="Generate New Graph" action={<span className="tag">Ready</span>}>
              <p className="model-sidebar-text">
                Pick one of the models listed here and start a new run from the create run page.
              </p>
              <Button variant="accent" onClick={() => navigate("/create-run")} style={{ width: "100%" }}>
                Create Run
              </Button>
            </Panel>
          </div>

          <Panel
            title="Model List"
            action={
              <div className="model-filter-bar">
                <form
                  className="model-search-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    setSearchTerm(searchInput.trim());
                  }}
                >
                  <Field label="Search">
                    <input
                      type="text"
                      className="field-input"
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      placeholder="Search models…"
                    />
                  </Field>
                  <Button type="submit" variant="neutral">
                    Search
                  </Button>
                </form>

                <Field label="Filter by">
                  <select
                    className="field-select"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="">None</option>
                    <option value="type">Type</option>
                    <option value="efficiency">Efficiency</option>
                  </select>
                </Field>

                <Button
                  variant="neutral"
                  disabled={!sortBy}
                  style={{ opacity: sortBy ? 1 : 0.5 }}
                  onClick={() => setInvert((v) => !v)}
                  title={sortBy ? "Invert current sort order" : "Select a filter field first"}
                >
                  {invert ? "Inverted ⇅" : "Invert"}
                </Button>
              </div>
            }
          >
            {loading && <p className="empty-note">Loading models…</p>}
            {error && <p className="empty-note" style={{ color: "var(--danger)" }}>{error}</p>}

            {!loading && !error && models.length === 0 && (
              <p className="empty-note">No models match this search.</p>
            )}

            {!loading && !error && models.length > 0 && (
              <div className="model-table-wrap">
                <table className="model-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Type</th>
                      <th>Efficiency</th>
                      <th>Parameters</th>
                      <th>Docs</th>
                      <th>Paper</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map((model, idx) => (
                      <tr key={model.id ?? idx}>
                        <td>{idx + 1}</td>
                        <td>
                          <button
                            type="button"
                            className="model-title-btn"
                            onClick={() => setSelectedModel(model)}
                          >
                            {model.type}
                          </button>
                        </td>
                        <td>
                          <span className={`tag status-${model.efficiency}`}>{model.efficiency}</span>
                        </td>
                        <td>{model.parameters}</td>
                        <td>
                          {model.documentation ? (
                            <a href={model.documentation} target="_blank" rel="noreferrer" className="model-table-link">
                              View
                            </a>
                          ) : (
                            <span className="model-table-empty">—</span>
                          )}
                        </td>
                        <td>
                          {model.paper ? (
                            <a href={model.paper} target="_blank" rel="noreferrer" className="model-table-link">
                              View
                            </a>
                          ) : (
                            <span className="model-table-empty">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>
        </div>
      </div>

      {selectedModel && (
        <Modal title={selectedModel.type} onClose={() => setSelectedModel(null)}>
          <div className="model-detail-grid">
            <Field label="Model ID">
              <span style={{ color: "var(--text)", fontSize: "0.85rem" }}>{selectedModel.id}</span>
            </Field>
            <Field label="Efficiency">
              <span className={`tag status-${selectedModel.efficiency}`}>{selectedModel.efficiency}</span>
            </Field>
            <Field label="Parameters">
              <span style={{ color: "var(--text)" }}>{selectedModel.parameters || "—"}</span>
            </Field>
            <Field label="Documentation">
              {selectedModel.documentation ? (
                <a href={selectedModel.documentation} target="_blank" rel="noreferrer" style={{ color: "var(--text)" }}>
                  {selectedModel.documentation}
                </a>
              ) : (
                <span style={{ color: "var(--text-faint)" }}>—</span>
              )}
            </Field>
            <Field label="Paper">
              {selectedModel.paper ? (
                <a href={selectedModel.paper} target="_blank" rel="noreferrer" style={{ color: "var(--text)" }}>
                  {selectedModel.paper}
                </a>
              ) : (
                <span style={{ color: "var(--text-faint)" }}>—</span>
              )}
            </Field>
          </div>
        </Modal>
      )}
    </div>
  );
}