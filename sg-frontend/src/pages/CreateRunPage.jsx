import { createRun } from "../api/runs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Panel } from "./ui/Panel-Light";
import { Button } from "./ui/Button";
import { Toggle } from "./ui/Toggle";
import { Field } from "./ui/Field";
import AttributeEditor from "./ui/attributes/AttributeEditor";
import { buildAttributeConfig } from "./ui/attributes/AttributeRules";
import bgImage from "../assets/bcg.png";
import "./css/tokens.css";
import "./css/ui.css";
import "./css/CreateRunPage.css";

export default function CreateRunPage() {
  const navigate = useNavigate();

  const [jobType, setJobType] = useState("ba");
  const [name, setName] = useState("");
  const [n, setN] = useState(30);
  const [m, setM] = useState(2);
  const [p, setP] = useState(0.1);
  const [seed, setSeed] = useState(42);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [nodeType, setNodeType] = useState("");
  const [edgeType, setEdgeType] = useState("");

  const [file, setFile] = useState(null);
  const [filepath, setFilepath] = useState("");
  const [uploading, setUploading] = useState(false);

  const [showAttributes, setShowAttributes] = useState(false);
  const [nodeAttributes, setNodeAttributes] = useState([]);
  const [edgeAttributes, setEdgeAttributes] = useState([]);

  const modelMap = {
    ba: "barabasi_albert",
    er: "erdos_renyi",
    ergm: "ergm",
  };
  const model = modelMap[jobType] || "ba";

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      let uploadedPath = filepath;

      if (jobType === "ergm") {
        if (!file) throw new Error("Please choose a file for ERGM");
        setUploading(true);
        uploadedPath = await uploadFile(file);
        setFilepath(uploadedPath);
        setUploading(false);
      }

      const payload = {
        name,
        job_type: jobType,
        model,
        params: {
          ...(jobType === "ba"
            ? { n: Number(n), m: Number(m), seed: Number(seed) }
            : jobType === "er"
            ? { n: Number(n), p: Number(p), seed: Number(seed) }
            : { filepath: uploadedPath, seed: Number(seed) }),
          schema: {
            node_type: nodeType || "node",
            edge_type: edgeType || "connected_to",
            ...(showAttributes ? {
              node_attributes: buildAttributeConfig(nodeAttributes),
              edge_attributes: buildAttributeConfig(edgeAttributes),
            } : {}),
          },
        },
      };

      const createdRun = await createRun(payload);
      navigate(`/runs/${createdRun.id}`);
    } catch (err) {
      setError(err.message || "Failed to create run");
    } finally {
      setUploading(false);
      setSubmitting(false);
    }
  }

  async function uploadFile(selectedFile) {
    const formData = new FormData();
    formData.append("file", selectedFile, selectedFile.name);

    const res = await fetch("http://localhost:8000/api/upload/", {
      method: "POST",
      body: formData,
    });

    const contentType = res.headers.get("content-type") || "";
    const bodyText = await res.text();

    if (!res.ok) {
      throw new Error(`Upload failed (${res.status}): ${bodyText.slice(0, 500)}`);
    }
    if (!contentType.includes("application/json")) {
      throw new Error(`Upload returned non-JSON response: ${bodyText.slice(0, 500)}`);
    }

    return JSON.parse(bodyText).filepath;
  }

  return (
    <div className="create-page">
      <div className="create-bg" style={{ backgroundImage: `url(${bgImage})` }} />
      <div className="create-content">
        <div className="create-panel-wrap">
          <Panel title="Create Run">
            <form onSubmit={handleSubmit} className="form-grid">
              <Field label="Name">
                <input className="field-input" value={name} onChange={(e) => setName(e.target.value)} placeholder="My graph run" required />
              </Field>

              <Field label="Job Type">
                <select className="field-select" value={jobType} onChange={(e) => setJobType(e.target.value)}>
                  <option value="ba">Barabasi-Albert</option>
                  <option value="er">Erdos-Renyi</option>
                  <option value="ergm">ERGM (fit from file)</option>
                </select>
              </Field>

              {jobType === "ergm" ? (
                <Field label="Input graph file" hint="Upload .mtx, .txt, or .csv edge list">
                  <input className="field-input" type="file" accept=".mtx,.txt,.csv" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
                </Field>
              ) : (
                <>
                  <Field label="n" hint="Number of nodes">
                    <input className="field-input" type="number" value={n} onChange={(e) => setN(e.target.value)} min="1" required />
                  </Field>

                  {jobType === "ba" ? (
                    <Field label="m" hint="Edges to attach per new node">
                      <input className="field-input" type="number" value={m} onChange={(e) => setM(e.target.value)} min="1" required />
                    </Field>
                  ) : (
                    <Field label="p" hint="Edge probability">
                      <input className="field-input" type="number" step="0.01" value={p} onChange={(e) => setP(e.target.value)} min="0" max="1" required />
                    </Field>
                  )}
                </>
              )}

              <Field label="seed" hint="For reproducibility">
                <input className="field-input" type="number" value={seed} onChange={(e) => setSeed(e.target.value)} />
              </Field>

              <Field label="Node type" hint="e.g. account, person, device">
                <input className="field-input" value={nodeType} onChange={(e) => setNodeType(e.target.value)} placeholder="account" />
              </Field>

              <Field label="Edge relationship" hint="e.g. friends, transacts_with">
                <input className="field-input" value={edgeType} onChange={(e) => setEdgeType(e.target.value)} placeholder="friends" />
              </Field>

              <div className="attr-toggle-row">
                <div>
                  <p className="attr-toggle-label">Node &amp; Edge Attributes</p>
                  <p className="attr-toggle-hint">Add optional generated properties</p>
                </div>
                <Toggle checked={showAttributes} onChange={() => setShowAttributes((v) => !v)} on="Enabled" off="Disabled" />
              </div>

              {showAttributes && (
                <div className="attr-editor-wrap">
                  <AttributeEditor label="Node attributes" rules={nodeAttributes} setRules={setNodeAttributes} />
                  <AttributeEditor label="Edge attributes" rules={edgeAttributes} setRules={setEdgeAttributes} />
                </div>
              )}

              <Button type="submit" variant="accent" disabled={submitting || uploading}>
                {uploading ? "Uploading…" : submitting ? "Creating…" : "Create Run"}
              </Button>

              {error && <p style={{ color: "#ff9c9c", margin: 0 }}>{error}</p>}
            </form>
          </Panel>
        </div>
      </div>
    </div>
  );
}