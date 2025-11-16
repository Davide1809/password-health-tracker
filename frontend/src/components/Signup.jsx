import React, { useState } from "react";
import { validateEmail, validatePassword, passwordRequirementsText } from "../utils/validators";
import { useNavigate } from "react-router-dom";
import { BACKEND_URL } from "../config";

export default function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordMeta, setPasswordMeta] = useState({
    length: false,
    upper: false,
    lower: false,
    number: false,
    symbol: false,
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  function handlePasswordChange(e) {
    const val = e.target.value;
    setPassword(val);
    setPasswordMeta(validatePassword(val));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    // client-side checks
    if (!validateEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    const passMeta = validatePassword(password);
    const passOk = Object.values(passMeta).every(Boolean);
    if (!passOk) {
      setError("Password does not meet security requirements.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.toLowerCase().trim(), password }),
      });

  const body = await res.json();
  console.log("Response status:", res.status);
  console.log("Response body:", body);

  if (!res.ok) {
    setError(body.message || "Registration failed. Please try again.");
    setLoading(false);
    return;
  }

      // success
      setSuccessMsg("Account created successfully! Redirecting…");
      // small delay to show confirmation
      setTimeout(() => {
        navigate("/dashboard");
      }, 900);
    } catch (err) {
      console.error("Signup error:", err);
      setError("Network error. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="signup-card">
      <h2>Create account</h2>

      <form onSubmit={handleSubmit} className="signup-form" noValidate>
        <label>
          Email
          <input
            type="email"
            name="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            aria-invalid={error && !validateEmail(email)}
          />
        </label>

        <label>
          Password
          <input
            type="password"
            name="password"
            value={password}
            onChange={handlePasswordChange}
            placeholder="Create a strong password"
            required
            aria-describedby="pw-requirements"
          />
        </label>

        <div id="pw-requirements" className="pw-requirements">
          <p>Password requirements:</p>
          <ul>
            {Object.entries(passwordRequirementsText).map(([key, text]) => (
              <li key={key} className={passwordMeta[key] ? "ok" : "bad"}>
                {passwordMeta[key] ? "✓" : "•"} {text}
              </li>
            ))}
          </ul>
        </div>

        {error && <div className="error">{error}</div>}
        {successMsg && <div className="success">{successMsg}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>
    </div>
  );
}