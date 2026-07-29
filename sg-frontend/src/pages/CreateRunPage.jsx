// import { useState } from "react";
// import { useNavigate } from "react-router-dom";
import { createRun } from "../api/runs";

import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
// import ForceGraph2D from "react-force-graph-2d";
// import { buildGraphData, computeMetrics, extraKeys } from "../utils/graphMetrics";
import {Panel} from "./ui/Panel-Light";
import {Button} from "./ui/Button";
import {Tag, StatusTag} from "./ui/Tag";
import {Toggle} from "./ui/Toggle";
import {Modal} from "./ui/Modal";
import {Field} from "./ui/Field"
import bgImage from "../assets/bcg.png";
import "./css/tokens.css";
import "./css/ui.css";
import "./css/CreateRunPage.css";

export default function CreateRunPage (){
  // parameters that will always be used

  const navigate = useNavigate();

  const [jobType, setJobType] = useState("ba");
  const [name, setName] = useState("");
  const [n, setN] = useState(30);
  const [m, setM] = useState(2);
  const [p, setP] = useState(0.1);
  const [seed, setSeed] = useState(42);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const model = jobType === "ba" ? "barabasi_albert" : "erdos_renyi";

    async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const payload = {
        name,
        job_type: jobType,
        model,
        params:
          jobType === "ba"
            ? { n: Number(n), m: Number(m), seed: Number(seed) }
            : { n: Number(n), p: Number(p), seed: Number(seed) },
      };

      const createdRun = await createRun(payload);
      navigate(`/runs/${createdRun.id}`);
    } catch (err) {
      setError(err.message || "Failed to create run");
    } finally {
      setSubmitting(false);
    }
  }


  return (
     <div className="create-page">
      <div className="create-bg" style={{ backgroundImage: `url(${bgImage})` }} />
        <div className="create-content">
          <div className="create-panel-wrap">
            <Panel title="Create Run" >
            <form onSubmit={handleSubmit} className="form-grid" >
              <Field label="Name">
                <input
                  className="field-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="My graph run"
                  required
                />
              </Field>

              <Field label="Job Type">
                <select
                  className="field-select"
                  value={jobType}
                  onChange={(e) => setJobType(e.target.value)}
                >
                  <option value="ba">Barabasi-Albert</option>
                  <option value="er">Erdos-Renyi</option>
                </select>
              </Field>

              <Field label="n" hint="Number of nodes">
                <input
                  className="field-input"
                  type="number"
                  value={n}
                  onChange={(e) => setN(e.target.value)}
                  min="1"
                  required
                />
              </Field>

              {jobType === "ba" ? (
                <Field label="m" hint="Edges to attach per new node">
                  <input
                    className="field-input"
                    type="number"
                    value={m}
                    onChange={(e) => setM(e.target.value)}
                    min="1"
                    required
                  />
                </Field>
              ) : (
                <Field label="p" hint="Edge probability">
                  <input
                    className="field-input"
                    type="number"
                    step="0.01"
                    value={p}
                    onChange={(e) => setP(e.target.value)}
                    min="0"
                    max="1"
                    required
                  />
                </Field>
              )}

              <Field label="seed" hint="For reproducibility">
                <input
                  className="field-input"
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(e.target.value)}
                />
              </Field>

              <Button type="submit" variant="accent" disabled={submitting}>
                {submitting ? "Creating…" : "Create Run"}
              </Button>

              {error && <p style={{ color: "#ff9c9c", margin: 0 }}>{error}</p>}
            </form>
          </Panel>
              




          </div>





        
        </div>

    </div>
  )

}