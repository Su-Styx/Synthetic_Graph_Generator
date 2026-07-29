// src/pages/DashboardPage.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authFetch } from "../api/authFetch";   // ⬅️ import the helper
import bgImage from "../assets/bcg.png";

export default function DashboardPage() {
  const username = localStorage.getItem("username") || "Unknown user";

  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // use this effect block to fetch runs on component mount
  useEffect(() => {
    async function fetchRuns() {
      setLoading(true);
      setError("");

      try {
        // ONE request using authFetch – it will refresh if needed
        const res = await authFetch("http://127.0.0.1:8000/api/runs/");
        if (!res.ok) {
          throw new Error("Failed to load runs");
        }

        const data = await res.json();

        // Filter to only this user's runs if your API returns all runs.
        const userRuns = Array.isArray(data)
          ? data.filter(
              (run) =>
                run.user === username ||
                run.owner === username ||
                !run.user // fallback if user field not present
            )
          : [];

        setRuns(userRuns);
      } catch (err) {
        setError("Could not load runs");
      } finally {
        setLoading(false);
      }
    }

    fetchRuns();
  }, [username]);

  return (
    <div
      style={{
        position: "relative",
        minHeight: "100vh",
        width: "100vw",
        overflow: "hidden",
        fontFamily: "Arial, sans-serif",
      }}
    >
      {/* Blurred background */}
      <div
        style={{
          minHeight: "100vh",
          width: "100vw",
          backgroundImage: `url(${bgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          filter: "blur(8px)",
        }}
      />

      {/* Profile circle (top-right) */}
      <Link
        to="/settings"
        style={{
          position: "absolute",
          top: "4%",
          right: "2%",
          width: "65px",
          height: "65px",
          borderRadius: "999px",
          background: "rgba(226, 220, 220, 0.22)",
          border: "1px solid rgba(255, 255, 255, 0.35)",
          backdropFilter: "blur(16px) saturate(140%)",
          WebkitBackdropFilter: "blur(16px) saturate(140%)",
          boxShadow:
            "0 18px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          textDecoration: "none",
          fontSize: "1.8rem",
          zIndex: 20,
        }}
      >
        👤
      </Link>

      {/* Main dashboard foreground (sidebar + table) */}
      <div
        style={{
          position: "absolute",
          top: "25%",
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          padding: "1.5rem 2rem",
          gap: "1.5rem",
          zIndex: 10,
          backgroundColor: "#9b2e2e88",
        }}
      >
        {/* Left sidebar (unchanged) */}
        <div
          style={{
            width: "500px",
            display: "flex",
            flexDirection: "column",
            backgroundColor: "rgba(122, 98, 187, 0.8)",
          }}
        >
          {/* Models List card */}
          <div
            style={{
              backgroundColor: "rgba(30, 30, 30, 0.8)",
              maxWidth: "50%",
              borderRadius: "24px",
              padding: "1rem",
              boxShadow: "0 12px 24px rgba(0, 0, 0, 0.5)",
              color: "white",
            }}
          >
            <div
              style={{
                backgroundColor: "rgba(204, 163, 80, 0.95)",
                borderRadius: "16px 16px 0 0",
                padding: "0.7rem 1rem",
                fontWeight: 600,
                textAlign: "center",
              }}
            >
              Models List
            </div>

            <div
              style={{
                marginTop: "0.9rem",
                backgroundColor: "rgba(240, 240, 240, 0.92)",
                borderRadius: "24px",
                padding: "2rem 1.5rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <button
                type="button"
                style={{
                  width: "90px",
                  height: "90px",
                  borderRadius: "24px",
                  border: "none",
                  backgroundColor: "rgba(204, 163, 80, 0.95)",
                  color: "white",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
                onClick={() => {
                  // Navigate to the graph generation page
                  window.location.href = "/models";
                }}
              >
                🔍 Browse
              </button>
            </div>
          </div>

          {/* Generate New Graph card */}
          <div
            style={{
              backgroundColor: "rgba(30, 30, 30, 0.8)",
              maxWidth: "50%",
              borderRadius: "24px",
              padding: "1rem",
              boxShadow: "0 12px 24px rgba(0, 0, 0, 0.5)",
              color: "white",
            }}
          >
            <div
              style={{
                backgroundColor: "rgba(72, 160, 72, 0.95)",
                borderRadius: "16px 16px 0 0",
                padding: "0.7rem 1rem",
                fontWeight: 600,
                textAlign: "center",
              }}
            >
              Generate New Graph
            </div>

            <div
              style={{
                marginTop: "0.9rem",
                backgroundColor: "rgba(240, 240, 240, 0.92)",
                borderRadius: "24px",
                padding: "2rem 1.5rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <button
                type="button"
                style={{
                  width: "90px",
                  height: "90px",
                  borderRadius: "24px",
                  border: "none",
                  backgroundColor: "rgba(72, 160, 72, 0.95)",
                  color: "white",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
                onClick={() => {
                  // Navigate to the graph generation page
                  window.location.href = "/create-run";
                }}
              >
                ＋ Generate
              </button>
            </div>
          </div>
        </div>

        {/* Right main table panel */}
        <div
          style={{
            flex: 1,
            backgroundColor: "#D9D9D9",
            borderRadius: "0px",
            padding: "0rem 2rem",
          }}
        >
          <div
            style={{
              borderBottom: "2px solid #080808",
              paddingBottom: "0.5rem",
              marginBottom: "1rem",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
            }}
          >
            <h2
              style={{
                margin: 0,
                fontSize: "1.8rem",
                letterSpacing: "0.08em",
                color: "#080808",
              }}
            >
              GENERATED GRAPHS -
            </h2>
            <span style={{ fontSize: "0.85rem", color: "#080808" }}>
              Name | Model | Status | Time started 
            </span>
          </div>

          {loading && <p>Loading runs…</p>}
          {error && <p style={{ color: "crimson" }}>{error}</p>}

          {!loading && !error && runs.length === 0 && (
            <p style={{ color: "#080808" }}>No runs yet.</p>
          )}

          {!loading && !error && runs.length > 0 && (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "0.95rem",
              }}
            >
              <tbody>
                {runs.map((run, idx) => (
                  <tr key={run.id ?? idx}>
                    <td
                      style={{
                        color: "#080808",
                        padding: "0.25rem",
                        borderBottom: "1px solid #020202",
                      }}
                    >
                      {idx + 1}
                    </td>

                    <td
                      style={{
                        padding: "0.25rem",
                        borderBottom: "1px solid #797878",
                        color: "#080808",
                        fontWeight: "bold",
                      }}
                      // linkto={`/runs/${run.id}`}  // Optional: if you want to make the name clickable
                    >
                      <a style={{color:"black", textDecoration:"underline", fontWeight:"bold"}} href={`/runs/${run.id}`}> {run.name} </a>
                    </td>
                    <td
                      style={{
                        padding: "0.25rem",
                        borderBottom: "1px solid #797878",
                        color: "#080808",
                      }}
                    >
                      {run.model}
                    </td>
                    <td
                      style={{
                        padding: "0.25rem",
                        borderBottom: "1px solid #797878",
                        color: "#080808",
                      }}
                    >
                      {run.status}
                    </td>
                    <td
                      style={{
                        padding: "0.25rem",
                        borderBottom: "1px solid #797878",
                        color: "#080808",
                      }}
                    >
                      {run.started_at || run.created_at || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}