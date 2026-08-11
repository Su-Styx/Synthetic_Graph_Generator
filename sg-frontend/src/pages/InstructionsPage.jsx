// src/pages/UsageInstructionsPage.jsx
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Panel } from "./ui/Panel-Light";
import { Button } from "./ui/Button";
import { StatusTag } from "./ui/Tag";
import bgImage from "../assets/bcg.png";
import "./css/tokens.css";
import "./css/ui.css";

const NAVBAR_HEIGHT = 88;

// Local toggle, matching the style/behaviour used on RunDetailPage.
// If you already have a shared ./ui/Toggle component, you can swap this
// out for: import { Toggle } from "./ui/Toggle";
const Toggle = ({ checked, onChange }) => (
  <button type="button" className="toggle" onClick={onChange}>
    {checked ? "Shown" : "Hidden"}
    <span className={`toggle-track ${checked ? "on" : ""}`}>
      <span className={`toggle-thumb ${checked ? "on" : ""}`} />
    </span>
  </button>
);

const SectionHeading = ({ children }) => (
  <h2
    style={{
      margin: "0 0 0.6rem 0",
      fontSize: "1.25rem",
      fontWeight: 700,
      color: "#ffffff",
      letterSpacing: "0.01em",
    }}
  >
    {children}
  </h2>
);

const SectionBody = ({ children, style }) => (
  <p
    style={{
      margin: "0 0 1.75rem 0",
    //   color: "var(--muted, #111827b9s)",
      fontSize: "0.98rem",
      lineHeight: 1.65,
      maxWidth: "760px",
      ...style,
    }}
  >
    {children}
  </p>
);

export default function UsageInstructionsPage() {
  const navigate = useNavigate();
  const [showFullInstructions, setShowFullInstructions] = useState(false);
  const bullettedlist=['Identify objective ','Select best model ','Identify parameters/ pre-requisites ','Navigate to CreateRunPage','Enter parameters/ details ','Wait for model to generate ',' Click on run from dashboard list ','Select a name','Verify the graph fulfills your criteria through Workload Query Suite','return to RunDetailsPage and download the right export format for you ','Done! :)',]

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
          pointerEvents: "none",
          zIndex: -1,
        }}
      />

      <main
        style={{
          position: "relative",
          minWidth: "99vw",
          minHeight: `calc(100vh - ${NAVBAR_HEIGHT}px)`,
          padding: `${NAVBAR_HEIGHT + 24}px 24px 48px`,
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
                Usage Instructions
              </h1>
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
              <Panel title="Models List" action={<StatusTag status="Reference" />}>
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
            </div>

            {/*
              Increased-opacity backdrop behind the instructions panel.
              Panel-Light renders a translucent card; this solid layer sits
              directly behind it so the card reads as more opaque without
              needing to touch the shared Panel-Light component. If Panel
              already forwards a `style` prop straight to its root element,
              you can delete this wrapper and instead pass
              style={{ background: "rgba(255,255,255,0.95)" }} to the
              <Panel> below directly.
            */}
            <div
              style={{
                position: "relative",
                borderRadius: "16px",
                background: "rgba(255, 255, 255, 0.4)",
                boxShadow: "0 14px 34px rgba(0,0,0,0.28)",
              }}
            >
              <Panel
                title={
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "1rem",
                      flexWrap: "wrap",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.6rem",
                      }}
                    >
                      <Toggle
                        checked={showFullInstructions}
                        onChange={() => setShowFullInstructions((v) => !v)}
                      />
                      <span
                        style={{
                          fontSize: "0.82rem",
                          color: "var(--muted, #4fb84b)",
                          letterSpacing: "0.03em",
                        }}
                      >
                        See Step-by-Step Instructions
                      </span>
                    </div>

                    <span>How to Use the Platform</span>
                  </div>
                }
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    minWidth: "100%",
                  }}
                >
                  {showFullInstructions && (
                    <div
                      style={{
                        borderTop: "1px solid rgba(0,0,0,0.08)",
                        borderBottom: "1px solid rgba(0,0,0,0.08)",
                        padding: "1rem 0",
                        marginBottom: "1.5rem",
                      }}
                    >
                      <p
                        style={{
                          margin: 0,
                          color: "#111827b9",
                          fontSize: "0.95rem",
                          lineHeight: 1.7,
                          maxWidth: "820px",
                        }}
                      >


                          <ol>
                            {bullettedlist.map((item, index) => (
                            <li key={item}>{item}</li>
                            ))}
                        </ol>
                      </p>
                    </div>
                  )}

                  <SectionHeading>How to pick a model</SectionHeading>
                  <SectionBody style={{color: "#111827b9"}} >
                    If you are confused about which model is best for your use-case, 
                    have a look at the model list and sort by tags to help you find 
                    the best one for your needs. 
                  </SectionBody>

                  <SectionHeading>How to generate a graph</SectionHeading>
                  <SectionBody style={{color: "#111827b9"}} >
                Parameters: If you are confused about what exactly a parameter means/does, 
                navigate to the models list, select your model and read the section on the model’s 
                parameters. 

                Source Data: Some graph generation models will require source data in particular formats, 
                please follow the directions at the submission box when creating your Run. 

                **Run-Time**: The time it takes for a model to generate your graph is generally dependent
                on two factors: 1. the model itself, how complex it is 2. How large of a graph you’re generating
                  </SectionBody>

                  <SectionHeading>How to preview a graph</SectionHeading>
                  <SectionBody style={{color: "#111827b9"}} >
                    If all you need to do is visualise a graph, head over to the QuickView Page.
                    For the best experience, only upload graphs of up to 1500 nodes and ideally 
                    with minimal attributes.
                  </SectionBody>

                  <SectionHeading>Generating attributes</SectionHeading>
                  <SectionBody style={{color: "#111827b9"}} >
                    If you need nodes to represent users, categories or… cats? Whilst edges represent
                     friendships, connections, etc…, Toggle the Node and Edge Attributes option at the
                      bottom of the CreateRun page, which allows for assigning the probabilities of 
                      different categorical attributes for both Nodes and Edges to be applied to a new, generated graph. 
                  </SectionBody>

                  <SectionHeading>Export Formats</SectionHeading>
                  <SectionBody style={{color: "#111827b9"}} >
                    Useful Export Format info goes here
                  </SectionBody>
                </div>
              </Panel>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}