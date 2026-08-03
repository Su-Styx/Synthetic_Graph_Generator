// src/App.jsx
// import { Link, Route, Routes, useNavigate } from "react-router-dom";
import { NavLink, Route, Routes, useNavigate, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignUpPage";
import CreateRunPage from "./pages/CreateRunPage";
import RunsPage from "./pages/RunsPage";
import RunDetailPage from "./pages/RunDetailPage";
import SettingsPage from "./pages/SettingsPage";
import AboutPage from "./pages/AboutPage";
import DashboardPage from "./pages/DashboardPage";
import WorkloadQueryPage from "./pages/WorkloadQueryPage";
import QuickViewPage from "./pages/QuickViewPage";


export default function App() {
  const navigate = useNavigate();
  const isLoggedIn = Boolean(localStorage.getItem("accessToken"));
  const location = useLocation();

  function handleLogout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    navigate("/login");
  }
  const hideNavOnRoutes = ["/"];          // home only for now
  const shouldShowNav = !hideNavOnRoutes.includes(location.pathname);

 return (
  <div style={{ minHeight: "100vh", width: "100%", fontFamily: "Arial, sans-serif" }}>
    {shouldShowNav && (
      <nav
      style={{
        zIndex: 1000,
        position: "absolute",
        top: "7.5%",
        left: "50%",
        transform: "translate(-50%, -50%)",   // pull back by half width & height

        width: "700px",
        height: "63px",
        padding: "0 1.2rem",
        display: "flex",
        alignItems: "center",
        gap: "0.6rem",
        zIndex: 10,
        // background: "rgba(160, 44, 40, 0.74)",
        background: "rgba(239, 248, 250, 0.29)",

        border: "1px solid rgba(253, 225, 225, 0.49)",
        borderRadius: "70px",
        // border: "1px solid rgba(255, 255, 255, 0.35)",
        backdropFilter: "blur(100px)",
        // WebkitBackdropFilter: "blur(16px) saturate(140%)",
        boxShadow:
          "0 5px 40px rgba(233, 222, 222, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3)",
      }}
    >


      {/* Logged-in links */}
      {isLoggedIn && (
        <>
          <NavLink
            to="/"
            style={({ isActive }) => ({
              zIndex:1000,
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.35rem 0.8rem",
              borderRadius: "999px",
              textDecoration: "none",
              color: "white",
              background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <span style={{ fontSize: "0.9rem" }}>+</span>
            <span>Home</span>
          </NavLink>
        <NavLink
            to="/dashboard"
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.35rem 0.8rem",
              borderRadius: "999px",
              textDecoration: "none",
              color: "white",
              background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <span style={{ fontSize: "0.9rem" }}>+</span>
            <span>Dashboard</span>
          </NavLink>
          <NavLink
            to="/create-run"
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.35rem 0.8rem",
              borderRadius: "999px",
              textDecoration: "none",
              color: "white",
              background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <span style={{ fontSize: "0.9rem" }}>+</span>
            <span>Create Run</span>
          </NavLink>

          <NavLink
            to="/quick-view"
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.35rem 0.8rem",
              borderRadius: "999px",
              textDecoration: "none",
              color: "white",
              background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <span style={{ fontSize: "0.9rem" }}>▤</span>
            <span>Quick View</span>
          </NavLink>

          <NavLink
            to="/settings"
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.35rem 0.8rem",
              borderRadius: "999px",
              textDecoration: "none",
              color: "white",
              background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
              fontWeight: isActive ? 600 : 500,
            })}
          >
            <span style={{ fontSize: "0.9rem" }}>⚙</span>
            <span>Settings</span>
          </NavLink>
        </>
      )}

      {/* Right side: auth / logout */}
      <div style={{ marginLeft: "auto", display: "flex", gap: "0.4rem" }}>
        {isLoggedIn ? (
          <button
            type="button"
            onClick={handleLogout}
            style={{
              padding: "0.35rem 0.9rem",
              borderRadius: "999px",
              border: "none",
              background: "rgba(255, 255, 255, 0.18)",
              color: "white",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        ) : (
          <>
            <NavLink
              to="/login"
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "0.3rem",
                padding: "0.35rem 0.7rem",
                borderRadius: "999px",
                textDecoration: "none",
                color: "white",
                background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
                fontWeight: isActive ? 600 : 500,
              })}
            >
              <span style={{ fontSize: "0.85rem" }}>●</span>
              <span>Login</span>
            </NavLink>

            <NavLink
              to="/signup"
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: "0.3rem",
                padding: "0.35rem 0.7rem",
                borderRadius: "999px",
                textDecoration: "none",
                color: "white",
                background: isActive ? "rgba(255, 255, 255, 0.18)" : "transparent",
                fontWeight: isActive ? 600 : 500,
              })}
            >
              <span style={{ fontSize: "0.85rem" }}>✚</span>
              <span>Sign up</span>
            </NavLink>
          </>
        )}
      </div>
    </nav>
    )}

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/create-run" element={<CreateRunPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/runs/:id" element={<RunDetailPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/workload-query" element={<WorkloadQueryPage />} />
        <Route path="/quick-view" element={<QuickViewPage />} />
      </Routes>
    </div>
  );
}