import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
// Questo componente probabilmente si chiama Signup.jsx o Registration.jsx

// *** Imposta l'URL del Backend Cloud Run ***
// Assicurati che questo URL sia ESATTAMENTE quello del tuo servizio backend
const BACKEND_URL = "https://password-backend-749522457256.us-central1.run.app"; 

export default function Signup() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Usa l'URL COMPLETO del backend
      const res = await fetch(`${BACKEND_URL}/api/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include', // Necessario per ricevere il cookie di sessione
      });

      if (res.ok) {
        // Registrazione e login avvenuti con successo
        localStorage.setItem("userEmail", email);
        navigate("/dashboard");
      } else {
        const data = await res.json();
        setError(data.message || "Registration failed. Please try again.");
      }
    } catch (err) {
      console.error("Signup Network Error:", err);
      setError("Network error. Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
        {/* ... (Il resto del codice di rendering del componente Signup) ... */}
        <div className="w-full max-w-md p-8 space-y-8 bg-white rounded-xl shadow-lg">
            <h2 className="text-center text-3xl font-extrabold text-gray-900">
                Create a new account
            </h2>
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                <div className="rounded-md shadow-sm -space-y-px">
                    <div>
                        <label htmlFor="email-address" className="sr-only">Email address</label>
                        <input
                            id="email-address"
                            name="email"
                            type="email"
                            autoComplete="email"
                            required
                            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                            placeholder="Email address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="sr-only">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            autoComplete="new-password"
                            required
                            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                </div>

                {error && <p className="text-red-500 text-sm text-center">{error}</p>}

                <div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                        {loading ? "Signing Up..." : "Sign Up"}
                    </button>
                </div>
                <div className="text-center">
                    <button
                        type="button"
                        onClick={() => navigate('/login')}
                        className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                    >
                        Already have an account? Sign In
                    </button>
                </div>
            </form>
        </div>
    </div>
  );
}