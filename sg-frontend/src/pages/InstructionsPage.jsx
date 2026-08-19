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
  const bullettedlist=['Think about what you’re trying to achieve!','Select the model that best fits your needs and data characteristics','Identify the parameters you need for running the model and/or any files','Navigate to CreateRunPage','Enter parameters/ details  ','Wait for model to generate ',' Click on run from dashboard list ','Select a name','Verify the graph meets your needs through Workload Query Suite','Return to RunDetailsPage and download the right export format for you ','Done :)',]

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

                    This section covers the two distinct types of node and edge attribute generation  

                    <h4>Node Type & Edge Relationships</h4>

                    The entries for node and edge relationships simply describes the label each item will recieve. For example, if the word ‘Student’ is written into the text box, nodes will display as Student 1, Student 2, etc… For Edges, the same concept applies, writing ‘Friends with’ into the text-box will result in the edge having a type of ‘Friends with’.
                    
                    
                    <h4> Node & Edge Attributes</h4>
                    This option is more advanced and is accessed by toggling a button beneath the Edge Relationships text box in the CreateRun page. 

                    Adding a Node attribute allows for the assignment of Categorical, Numeric or Timestamps to a Node’s attributes. For example, selecting the Categorical option and entering ‘Job’ in the first text box, then ‘Fireman’ in the second and leaving the last empty, will create a new attribute for every node, that is of category ‘Job’ and the value for all users is set to ‘Fireman’. The same applies for edges. 

                    Additionally, if you wish to assign one of a list of job titles for each node, such as 10% being Firemen, 30 % being Police, 40% being Teachers and 20% being Doctors, you can set the first box to ‘Job’, the second box to ‘Fireman,Police,Teacher,Doctor’ and the last to 0.1,0.3,0.4,0.2. This will result in the stochastic assignment of Job titles to nodes randomly.
                  </SectionBody>

                  <SectionHeading>Export Formats</SectionHeading>
                  <SectionBody style={{color: "#111827b9"}} >
                    <h4>CSV</h4>
                    The CSV format is a simple, widely supported format that can be opened in most tabular
                    software such as Microsoft Excel. Many Python and R libraries support CSV such as
                    NetworkX and pandas, enabling easy data analysis, processing, and utility of the CSV
                    file. CSV files are valuable for users who want easy, flexible data, without the need for
                    a graph database or specialist processing tools.

                    {/* <nl></nl> */}

                    <h4> JSON</h4>
                    The JSON format is highly prevalent across the web-development domain, for its
                    simplicity in structural representation of its contents. More specifically, it is easy and
                    efficient to parse, whilst preserving any number of attributes for objects represented.
                    JSON allows for easy integration and exchange across web APIs and processing through
                    front-end or back-end applications. JavaScript tooling, REST APIs and many graph-
                    visualisation libraries support JSON natively. In practice, the highly structured format
                    of JSON and powerful inter-operability across web-technologies allows for potential
                    user-automation of processing tasks without the need of manual format conversion.

                    <h4>Neo4j</h4>
                    The Neo4j database format stores string representations of nodes, relationships and
                    properties in place of a table/tabular representation. Neo4j allows for a more efficient
                    way of storing and querying relationships. Unlike a traditional relational database,
                    Neo4j does not use JOIN queries, relationships are stored alongside the nodes. In
                    practice, this is valuable when analysing data to discover deeply-rooted relationships
                    between different nodes or unforseen connections between distant items through Cypher
                    queries. Exporting a graph in the Neo4j format ensures the graph is ready to use in a
                    property-graph database environment without the need for manual conversion methods,
                    a complex task for non-professional users. Dedicated graph databases are generally
                    better suited to large, real-world graphs than traditional, relational databases.

                    <h4> RDF</h4>
                    The Resource Description Framework (RDF) represents data as subject, predicate,
                    object triples. RDF offers value in its support for semantic-web and knowled-graph use
                    cases, which greatly beenfit from its formal structure and relationship declaration. This
                    particular schema allows for greater expressiveness in terms of complex relationships
                    between different objects. RDF is part of a greater W3C ecosystem, which allows for
                    seamless integration of generated graphs into frameworks such as OWL for ontoloties
                    and SPARQL for querying (graphwise). Unlike other export formats, RDF is uniquely
                    well-suited for enabling semantic web-interoperability and graph analysis in supported
                    workflows.
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