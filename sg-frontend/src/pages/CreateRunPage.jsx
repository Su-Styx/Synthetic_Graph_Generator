import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRun } from "../api/runs";

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
            ? {
                n: Number(n),
                m: Number(m),
                seed: Number(seed),
              }
            : {
                n: Number(n),
                p: Number(p),
                seed: Number(seed),
              },
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
    <div>
      <h2>Create Run</h2>

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem", maxWidth: "420px" }}>
        <label>
          Name
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My graph run"
            required
          />
        </label>

        <label>
          Job Type
          <select value={jobType} onChange={(e) => setJobType(e.target.value)}>
            <option value="ba">Barabasi-Albert</option>
            <option value="er">Erdos-Renyi</option>
          </select>
        </label>

        <label>
          n
          <input
            type="number"
            value={n}
            onChange={(e) => setN(e.target.value)}
            min="1"
            required
          />
        </label>

        {jobType === "ba" ? (
          <label>
            m
            <input
              type="number"
              value={m}
              onChange={(e) => setM(e.target.value)}
              min="1"
              required
            />
          </label>
        ) : (
          <label>
            p
            <input
              type="number"
              step="0.01"
              value={p}
              onChange={(e) => setP(e.target.value)}
              min="0"
              max="1"
              required
            />
          </label>
        )}

        <label>
          seed
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(e.target.value)}
          />
        </label>

        <button type="submit" disabled={submitting}>
          {submitting ? "Creating..." : "Create Run"}
        </button>

        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      </form>
    </div>
  );
}