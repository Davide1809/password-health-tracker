import React from "react";
import { useNavigate } from "react-router-dom";

export default function Welcome() {   // ✅ default export
  const navigate = useNavigate();

  return (
    <div className="welcome-card">
      <h1>Welcome to Password Health Tracker</h1>
      <p>Secure your passwords and track their strength easily!</p>
      <div className="welcome-buttons">
        <button onClick={() => navigate("/signup")}>Sign Up</button>
        <button onClick={() => navigate("/login")}>Login</button>
      </div>
    </div>
  );
}