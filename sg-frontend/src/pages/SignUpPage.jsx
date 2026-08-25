import { useState } from "react";
import { useNavigate } from "react-router-dom";
import bgImage from "../assets/bcg.png";

export default function SignupPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      // 1. Create user
      const signupRes = await fetch("http://127.0.0.1:8000/api/signup/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const signupData = await signupRes.json();

      if (!signupRes.ok) {
        setError("Signup failed");
        return;
      }

      // 2. Immediately log in to get tokens
      const loginRes = await fetch("http://127.0.0.1:8000/api/token/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const loginData = await loginRes.json();

      if (!loginRes.ok) {
        setError("Account created, but login failed");
        return;
      }

      localStorage.setItem("accessToken", loginData.access);
      localStorage.setItem("refreshToken", loginData.refresh);
      localStorage.setItem("username", username);

      // 3. Redirect to create-run
      navigate("/create-run");
    } catch (err) {
      setError("Signup failed");
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100vw",
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
      {/* Center frosted glass card */}
      <div
        style={{
          width: "18%",
          height: "22%",
          padding: "1.5rem 1rem",
          width: "18%",
          height: "22%",

          padding: "1.5rem 1rem",
          // more glass-like fill: translucent tint instead of solid red
          background: "rgba(160, 44, 40, 0.74)",

          // frosted glass edge
          // borderRadius: "18px",
          // border: "1px solid rgba(253, 225, 225, 0.49)",

          color: "white",

          // stronger blur + saturation for the background image
          backdropFilter: "blur(10px) saturate(0%)",
          WebkitBackdropFilter: "blur(1px) saturate(140%)",

          // // layered shadow for depth + subtle inner glow
          boxShadow:
            "0 5px 20px rgba(224, 59, 59, 0.53), inset 0 5px 10px rgba(224, 59, 59, 0.53),",
          }}
      >
        <h2 style={{ margin: 0, marginBottom: "1rem", fontSize: "2rem" }}>
          Sign up
        </h2>

        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
          }}
        >
          <label style={{ display: "flex", flexDirection: "column", fontSize: "0.95rem" }}>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                marginTop: "0.25rem",
                padding: "0.4rem 0.5rem",
                borderRadius: "4px",
                border: "none",
              }}
              required
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", fontSize: "0.95rem" }}>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                marginTop: "0.25rem",
                padding: "0.4rem 0.5rem",
                borderRadius: "4px",
                border: "none",
              }}
              required
            />
          </label>

          <button
            type="submit"
            style={{
              marginTop: "0.75rem",
              padding: "0.5rem",
              borderRadius: "4px",
              border: "none",
              backgroundColor: "rgba(255, 255, 255, 0.9)",
              color: "#802828",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            Create account
          </button>

          {error && (
            <p style={{ color: "crimson", marginTop: "0.5rem" }}>{error}</p>
          )}
        </form>
      </div>
    </div>
  );
}