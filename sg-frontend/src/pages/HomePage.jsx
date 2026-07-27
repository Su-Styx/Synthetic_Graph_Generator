// src/pages/HomePage.jsx
import { Link } from "react-router-dom";
import bgImage from "../assets/bcg.png";
const arrowSize = "2.5rem";


export default function HomePage() {
  return (
    <div
      className="home-root"
      style={{
        minHeight: "100vh",
        width: "100vw",            // ensure full width
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        backgroundImage: `url(${bgImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      {/* Top‑right login */}
      <Link
        to="/login"
        style={{
          position: "absolute",
          top: "1rem",
          right: "1rem",
          padding: "0.5rem 1rem",
          backgroundColor: "rgba(160, 40, 40, 0.85)",
          color: "white",
          textDecoration: "none",
          fontWeight: "500",
        }}
      >
        Login
      </Link>

      {/* Center frosted card */}
      <div
        style={{
          width: "18%",
          // maxWidth: "400px",
          height: "19%",
          // maxHeight: "30%",
          // maxHeight: "350px",

          padding: "0rem 0.8rem",
          backgroundColor: "rgba(160, 40, 40, 0.65)",
          color: "white",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          boxShadow: "0 24px 40px rgba(0, 0, 0, 0.6)",
        }}
      >
        <div style={{ marginBottom: "1rem" }}>
          <h1 style={{ paddingTop: ".35rem", margin: 0, fontSize: "3rem", fontWeight: "700" }}>
            Graph Gen.
          </h1>
          <p style={{ marginTop: "0rem", fontSize: "1.3rem" }}>Simple.</p>
        </div>

        <div
  style={{
    display: "flex",
    alignItems: "flex-end",   // align arrow with bottom of list
    marginTop: "2.8rem",
  }}
>
  {/* Left: vertical list of links */}
  <div
    style={{
      display: "grid",
      gridAutoRows: "min-content",
      gap: "0.4rem",
      fontSize: "1.1rem",
      paddingBottom: ".6rem", 
    }}
  >
    <span>Home</span>
    <span>About</span>
    <span>Models</span>
    <span>Products</span>
  </div>

  {/* Right: arrow aligned with last item */}
  <span
    style={{
      marginLeft: "auto",     // pushes arrow to the right edge
      fontSize: arrowSize,    // configurable size
      paddingLeft: "1rem",    // small space between list and arrow
      // paddingBottom: "0.1rem",  // aligns arrow with bottom of list
    }}
  >
    ↓
  </span>
</div>
      </div>
    </div>
  );
}