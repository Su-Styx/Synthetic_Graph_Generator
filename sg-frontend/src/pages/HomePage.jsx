// src/pages/HomePage.jsx
import { Link } from "react-router-dom";
import bgImage from "../assets/bcg.png";
const arrowSize = "2.5rem";


export default function HomePage() {

  const isLoggedIn = Boolean(localStorage.getItem("accessToken"));
  const buttonLabel = isLoggedIn ? "Me" : "Login";
  const buttonTarget = isLoggedIn ? "/settings" : "/login"; // or "/profile"
  const cornerSquareSize = 40;
  const dashLabel =isLoggedIn ? "Dashboard" : "Home";
  const dashTarget = isLoggedIn ? "/dashboard" : "/home"; // or "/profile"S
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
        to={buttonTarget}
        style={{
          position: "absolute",
          top: "1rem",
          right: "1rem",
          padding: "0.9rem 1rem",
          // background: "rgba(160, 44, 40, 0.74)",
          background: "rgba(236, 232, 231, 0.74)",
          color: "white",
          backdropFilter: "blur(10px) saturate(0%)",
          WebkitBackdropFilter: "blur(1px) saturate(140%)",
          textDecoration: "none",
          fontWeight: "500",
        }}
      >
        {buttonLabel}
      </Link>

      {/* Center frosted card */}
      <div
      style={{

  width: "19%",
  height: "25%",
  minWidth: "300px",
  minHeight: "275px",
  // display: "flex",

  padding: ".2rem .5rem",
  
  // more glass-like fill: translucent tint instead of solid red
  // background: "rgba(160, 44, 40, 0.74)",
  background: "rgba(239, 248, 250, 0.57)",
  // backdropFilter: "blur(0px) saturate(0%)",

  // frosted glass edge
  borderRadius: "1px",
  border: "1px solid rgba(253, 225, 225, 0.49)",

  color: "white",

  // stronger blur + saturation for the background image
  backdropFilter: "blur(6.5px) saturate(6%)",
  WebkitBackdropFilter: "blur(1px) saturate(140%)",

  // // layered shadow for depth + subtle inner glow
  // boxShadow:
  //   "0 5px 20px rgba(224, 59, 59, 0.53), inset 0 5px 10px rgba(224, 59, 59, 0.53),",
}}>
  {/* Corner square */}
    <div
    style={{
      position: "absolute",
      top: -(cornerSquareSize / 2),   // move up by half its size
      right: -(cornerSquareSize / 2), // move right by half its size
      width: cornerSquareSize,
      height: cornerSquareSize,
      backgroundColor: "rgb(255, 255, 255)",
      boxShadow: "0 8px 16px rgba(0, 0, 0, 0.4)",
    }}

  />
  <div
    style={{
      position: "absolute",
      bottom: -20,           // push a little below the card
      left: -20,              // a bit outside to the left
      width: 121,
      height: 10,
      backgroundColor: "rgb(240, 240, 240)",
    }}
  />
  <div
    style={{
      position: "absolute",
      bottom: -20,           // further down
      left: -20,              // same x as the horizontal line
      width: 10,
      height: 121,
      backgroundColor: "rgb(240, 240, 240)",
    }}
  />

        <div style={{ marginBottom: "1rem" }}>
          <h1 style={{ paddingTop: ".2rem", margin: 0, color: "rgb(253, 253, 253)", fontSize: "3rem", fontWeight: "900" }}>
            Graph Gen.
          </h1>
          <p style={{ marginTop: "0rem", fontSize: "1.3rem" }}>Simple.</p>
        </div>

        <div
  style={{
    display: "flex",
    alignItems: "flex-end",   // align arrow with bottom of list
    marginTop: "4.5rem",
  }}
>
  {/* Left: vertical list of links */}
  <div
    style={{
      display: "grid",
      gridAutoRows: "min-content",
      gap: "0.2rem",
      fontSize: "1.1rem",
      paddingBottom: ".4rem", 
      colour: "white",
    }}
  >
    <Link to={dashTarget} style={{color: "white", textDecoration: "none"}}>
      {dashLabel} 
    </Link>
    <Link to="/about" style={{color: "white", textDecoration: "none"}}>
      About
    </Link>
    <Link to="/models" style={{color: "white", textDecoration: "none"}}>
      Models
    </Link>
    <Link to="/products" style={{color: "white", textDecoration: "none"}}>
      Products
    </Link>
    {/* {isLoggedIn ? (
          <Link to="/dashboard" style={{color: "white", textDecoration: "none"}}>
            Dashboard
          </Link>
        ) :(<></>)} */}
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