import React, { useState } from "react";
import { validateEmail } from "../utils/validators";
import { useNavigate } from "react-router-dom";
import { BACKEND_URL } from "../config";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!validateEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const body = await res.json();
      if (!res.ok) {
        setError(body.message || "Login failed. Please try again.");
        setLoading(false);
        return;
      }

      // ✅ Only access localStorage in the browser
      if (typeof window !== "undefined") {
        localStorage.setItem("userEmail", email);
      }

      setSuccessMsg("Login successful! Redirecting…");
      setTimeout(() => {
        navigate("/dashboard");
      }, 900);
    } catch (err) {
      console.error("Login error:", err);
      setError("Network error. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-card">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="login-form" noValidate>
        <label>
          Email
          <input
            type="email"
            name="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
        </label>

        {error && <div className="error">{error}</div>}
        {successMsg && <div className="success">{successMsg}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Logging in…" : "Log in"}
        </button>
      </form>
    </div>
  );
}