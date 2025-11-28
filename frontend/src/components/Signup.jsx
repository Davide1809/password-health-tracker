import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
// Questo componente probabilmente si chiama Signup.jsx o Registration.jsx

// *** Imposta l'URL del Backend Cloud Run ***
// Assicurati che questo URL sia ESATTAMENTE quello del tuo servizio backend
const BACKEND_URL = "https://password-backend-749522457256.us-central1.run.app"; 

export default function Signup() {
  const navigate = useNavigate();
  // 1. ADD STATE FOR THE USER NAME
  const [name, setName] = useState(""); 
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
        // 2. INCLUDE THE NAME FIELD IN THE REQUEST BODY (backend expects 'user_name')
        body: JSON.stringify({ 
            user_name: name, // Mapped 'name' state to 'user_name' for backend
            email, 
            password 
        }),
        credentials: 'include', // Necessario per ricevere il cookie di sessione
      });

      if (res.ok) {
        // Registrazione e login avvenuti con successo
        localStorage.setItem("userEmail", email);
        navigate("/dashboard");
      } else {
        const data = await res.json();
        // The error message from the backend will now be displayed here:
        // Either "Missing required fields" (if something is still empty) 
        // OR "User already exists" (if trying to register an old user)
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
    // Updated container to use dark background for better visual matching (based on your screenshots)
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="w-full max-w-md p-8 space-y-8 bg-gray-800 rounded-xl shadow-2xl text-white">
            <h2 className="text-center text-3xl font-extrabold text-indigo-400 flex items-center justify-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2zm0 4a3 3 0 1 1 0 6 3 3 0 0 1 0-6zm0 14.4c-3 0-5.6-.96-7.38-2.58A8 8 0 0 1 4 12a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1 8 8 0 0 1-1.62 5.82c-1.78 1.62-4.38 2.58-7.38 2.58z"/></svg>
                Create an Account
            </h2>
            
            {/* Error Message Display */}
            {error && (
                <div className="bg-red-900 bg-opacity-30 border border-red-600 text-red-300 p-3 rounded-md text-sm text-center">
                    {error}
                </div>
            )}

            <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
                <div className="rounded-md shadow-sm space-y-3">
                    
                    {/* 3. ADD INPUT FIELD FOR NAME (Your Name) */}
                    <div>
                        <label htmlFor="user-name" className="text-sm font-medium text-gray-300">Your Name</label>
                        <input
                            id="user-name"
                            name="user-name"
                            type="text"
                            autoComplete="name"
                            required
                            className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-700 mt-1"
                            placeholder="Your Name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>

                    <div>
                        <label htmlFor="email-address" className="text-sm font-medium text-gray-300">Email</label>
                        <input
                            id="email-address"
                            name="email"
                            type="email"
                            autoComplete="email"
                            required
                            className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-700 mt-1"
                            placeholder="Email address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    
                    <div>
                        <label htmlFor="password" className="text-sm font-medium text-gray-300">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            autoComplete="new-password"
                            required
                            className="appearance-none relative block w-full px-3 py-2 border border-gray-600 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-700 mt-1"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                </div>

                {/* NOTE: I removed the complex password requirements block for simplicity,
                   but you can add it back if you wish. The backend will enforce strength anyway. */}

                <div className="pt-4">
                    <button
                        type="submit"
                        disabled={loading}
                        className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-lg font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition duration-150 shadow-lg shadow-indigo-500/50"
                    >
                        {loading ? "Signing Up..." : "Sign Up"}
                    </button>
                </div>
                <div className="text-center mt-4">
                    <p className="text-sm text-gray-400">
                        Already have an account? 
                        <button
                            type="button"
                            onClick={() => navigate('/login')}
                            className="ml-1 text-indigo-400 hover:text-indigo-300 font-medium transition duration-150"
                        >
                            Log In here
                        </button>
                    </p>
                </div>
            </form>
        </div>
    </div>
  );
}