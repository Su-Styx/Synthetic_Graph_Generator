// src/App.jsx
import { Link, Route, Routes, useNavigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignUpPage";
import CreateRunPage from "./pages/CreateRunPage";
import RunsPage from "./pages/RunsPage";
import RunDetailPage from "./pages/RunDetailPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  const navigate = useNavigate();
  const isLoggedIn = Boolean(localStorage.getItem("accessToken"));

  function handleLogout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    navigate("/login");
  }

 return (
  <div style={{ minHeight: "100vh", width: "100%", fontFamily: "Arial, sans-serif" }}>
      <nav
        style={{
          position: "absolute",
          top: "1rem",
          left: "1rem",
          display: "flex",
          gap: "1rem",
          zIndex: 10,
        }}
      >
        <Link to="/">Home</Link>

        {isLoggedIn && (
          <>{/* links to stuff when logge di */}
            <Link to="/create-run">Create Run</Link>
            <Link to="/runs">Runs</Link>
            <Link to="/settings">Settings</Link>
          </>
        )}

        {isLoggedIn ? (
          <button type="button" onClick={handleLogout}>
            Logout
          </button>
        ) : (
          <>
            
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign up</Link>
            
          </>
        )}
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/create-run" element={<CreateRunPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/runs/:id" element={<RunDetailPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </div>
  );
}