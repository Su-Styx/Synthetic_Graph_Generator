// src/pages/DashboardPage.jsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authFetch } from "../api/authFetch";
import { Panel } from "./ui/Panel-Light";
import { Button } from "./ui/Button";
import { StatusTag } from "./ui/Tag";
import bgImage from "../assets/bcg.png";
import "./css/tokens.css";
import "./css/ui.css";

const NAVBAR_HEIGHT = 88;

export default function DashboardPage() {
  const navigate = useNavigate();
  const username = localStorage.getItem("username") || "Unknown user";

  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchRuns() {
      setLoading(true);
      setError("");

      try {
        const res = await authFetch("http://127.0.0.1:8000/api/runs/");
        if (!res.ok) {
          throw new Error("Failed to load runs");
        }

        const data = await res.json();

        const userRuns = Array.isArray(data)
          ? data.filter(
              (run) =>
                run.user === username ||
                run.owner === username ||
                !run.user
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
    <>
      <div
        style={{
          position: "fixed",
          inset: 0,
          backgroundImage: `url(${bgImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          filter: "blur(8px)",
          transform: "scale(1.03)",
          pointerEvents: "none",
          zIndex: -2,
        }}
      />

      <div
        style={{
          position: "fixed",
          inset: 0,
          // background:
            // "linear-gradient(180deg, rgba(14,16,20,0.42) 0%, rgba(14,16,20,0.60) 100%)",
          pointerEvents: "none",
          zIndex: -1,
        }}
      />

      <main
        style={{
          position: "relative",
          minWidth: "99vw",
          minHeight: `calc(100vh - ${NAVBAR_HEIGHT}px)`,
          padding: `${NAVBAR_HEIGHT + 24}px 24px 24px`,
          boxSizing: "border-box",
        }}
      >
        <Link
          to="/settings"
          style={{
            position: "fixed",
            top: `${NAVBAR_HEIGHT + 12}px`,
            right: "24px",
            width: "60px",
            height: "60px",
            borderRadius: "999px",
            background: "rgba(255,255,255,0.14)",
            border: "1px solid rgba(255,255,255,0.22)",
            backdropFilter: "blur(16px)",
            WebkitBackdropFilter: "blur(16px)",
            boxShadow: "0 14px 34px rgba(0,0,0,0.28)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            textDecoration: "none",
            fontSize: "1.5rem",
            zIndex: 20,
          }}
        >
          👤
        </Link>

        <div
          style={{
            maxWidth: "1400px",
            margin: "0 auto",
            display: "flex",
            flexDirection: "column",
            gap: "18px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
              gap: "16px",
              color: "white",
              paddingRight: "88px",
              
            }}
          >
            <div>
              <div
                style={{
                  fontSize: "0.82rem",
                  letterSpacing: "0.16em",
                  textTransform: "uppercase",
                  opacity: 0.8,
                  marginBottom: "0.45rem",
                }}
              >
                Graph Generation Workspace
              </div>

              <h1
                style={{
                  margin: 0,
                  fontSize: "2rem",
                  lineHeight: 1.05,
                  letterSpacing: "0.04em",
                }}
              >
                Dashboard
              </h1>
            </div>

            <div
              style={{
                fontSize: "0.92rem",
                color: "rgba(255,255,255,0.88)",
                whiteSpace: "nowrap",
              }}
            >
              Signed in as <strong>{username}</strong>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "320px minmax(0, 1fr)",
              gap: "18px",
              alignItems: "start",
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "18px",
              }}
            >
              <Panel title="Models List" action={<StatusTag status={`${runs.length} runs`} />}>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "14px",
                  }}
                >
                  <p
                    style={{
                      margin: 0,
                      color: "var(--muted, #6b7280)",
                      fontSize: "0.95rem",
                      lineHeight: 1.5,
                    }}
                  >
                    Browse the available graph generation models and inspect their
                    parameters before starting a run.
                  </p>

                  <Button
                    type="button"
                    variant="neutral"
                    onClick={() => navigate("/models")}
                    style={{ width: "100%" }}
                  >
                    Browse Models
                  </Button>
                </div>
              </Panel>

              <Panel title="Generate New Graph" action={<StatusTag status="Ready" />}>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "14px",
                    
                  }}
                >
                  <p
                    style={{
                      margin: 0,
                      color: "var(--muted, #6b7280)",
                      fontSize: "0.95rem",
                      lineHeight: 1.5,
                    }}
                  >
                    Create a new run using BA, ER, or ERGM generation and follow
                    it through to completion from the run detail view.
                  </p>

                  <Button
                    type="button"
                    variant="accent"
                    onClick={() => navigate("/create-run")}
                    style={{ width: "100%" }}
                  >
                    Create Run
                  </Button>
                </div>
              </Panel>
            </div>

            <Panel

              title="Generated Graphs"
              
              
              action={
                <span
                  style={{
                    fontSize: "0.82rem",
                    color: "var(--muted, #6b7280)",
                    letterSpacing: "0.03em",
                    // height: ".5rem",
                    // minWidth: "1800px",
                  }}
                >
                  Name · Model · Status · Time started
                </span>
              }
            >
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  height: `calc(100vh - ${NAVBAR_HEIGHT + 170}px)`,
                  // width: "1800px",
                  minHeight: "420px",
                  minWidth: "100%",
                }}
              > 
                {loading && (
                  <p style={{ margin: 0, color: "#111827" }}>Loading runs…</p>
                )}

                {error && (
                  <p style={{ margin: 0, color: "crimson" }}>{error}</p>
                )}

                {!loading && !error && runs.length === 0 && (
                  <p style={{ margin: 0, color: "#111827" }}>No runs yet.</p>
                )}

                {!loading && !error && runs.length > 0 && (
                  <div
                    style={{
                      flex: 1,
                      minHeight: 0,
                      overflowY: "auto",
                      overflowX: "hidden",
                      borderTop: "1px solid rgba(0,0,0,0.08)",
                      marginTop: "0.5rem",
                    }}
                  >
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        fontSize: "0.95rem",
                      }}
                    >
                      <thead
                        style={{
                          position: "sticky",
                          top: 0,
                          background: "rgba(255,255,255,0.97)",
                          zIndex: 2,
                        }}
                      >
                        <tr>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "0.7rem 0.4rem",
                              fontSize: "0.78rem",
                              letterSpacing: "0.08em",
                              textTransform: "uppercase",
                              color: "#6b7280",
                              borderBottom: "1px solid rgba(0,0,0,0.08)",
                            }}
                          >
                            #
                          </th>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "0.7rem 0.4rem",
                              fontSize: "0.78rem",
                              letterSpacing: "0.08em",
                              textTransform: "uppercase",
                              color: "#6b7280",
                              borderBottom: "1px solid rgba(0,0,0,0.08)",
                            }}
                          >
                            Name
                          </th>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "0.7rem 0.4rem",
                              fontSize: "0.78rem",
                              letterSpacing: "0.08em",
                              textTransform: "uppercase",
                              color: "#6b7280",
                              borderBottom: "1px solid rgba(0,0,0,0.08)",
                            }}
                          >
                            Model
                          </th>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "0.7rem 0.4rem",
                              fontSize: "0.78rem",
                              letterSpacing: "0.08em",
                              textTransform: "uppercase",
                              color: "#6b7280",
                              borderBottom: "1px solid rgba(0,0,0,0.08)",
                            }}
                          >
                            Status
                          </th>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "0.7rem 0.4rem",
                              fontSize: "0.78rem",
                              letterSpacing: "0.08em",
                              textTransform: "uppercase",
                              color: "#6b7280",
                              borderBottom: "1px solid rgba(0,0,0,0.08)",
                            }}
                          >
                            Time started
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        {runs.map((run, idx) => (
                          <tr key={run.id ?? idx}>
                            <td
                              style={{
                                padding: "0.8rem 0.4rem",
                                borderBottom: "1px solid rgba(0,0,0,0.06)",
                                color: "#111827",
                                verticalAlign: "middle",
                              }}
                            >
                              {idx + 1}
                            </td>

                            <td
                              style={{
                                padding: "0.8rem 0.4rem",
                                borderBottom: "1px solid rgba(0,0,0,0.06)",
                                verticalAlign: "middle",
                              }}
                            >
                              <Link
                                to={`/runs/${run.id}`}
                                style={{
                                  color: "#111827",
                                  textDecoration: "underline",
                                  fontWeight: 700,
                                }}
                              >
                                {run.name}
                              </Link>
                            </td>

                            <td
                              style={{
                                padding: "0.8rem 0.4rem",
                                borderBottom: "1px solid rgba(0,0,0,0.06)",
                                verticalAlign: "middle",
                              }}
                            >
                              <StatusTag status={run.model} />
                            </td>

                            <td
                              style={{
                                padding: "0.8rem 0.4rem",
                                borderBottom: "1px solid rgba(0,0,0,0.06)",
                                verticalAlign: "middle",
                              }}
                            >
                              <StatusTag status={run.status} />
                            </td>

                            <td
                              style={{
                                padding: "0.8rem 0.4rem",
                                borderBottom: "1px solid rgba(0,0,0,0.06)",
                                color: "#111827",
                                verticalAlign: "middle",
                                whiteSpace: "nowrap",
                              }}
                            >
                              {run.started_at || run.created_at || "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </Panel>
          </div>
        </div>
      </main>
    </>
  );
}