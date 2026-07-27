import { useState } from "react";
import { useNavigate } from "react-router-dom";

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

      // 3. Redirect to create-runs
      navigate("/create-run");
    } catch (err) {
      setError("Signup failed");
    }
  }

  return (
    <div>
      <h2>Sign up</h2>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem", maxWidth: "320px" }}>
        <label>
          Username
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        <button type="submit">Create account</button>

        {error && <p style={{ color: "crimson" }}>{error}</p>}
      </form>
    </div>
  );
}