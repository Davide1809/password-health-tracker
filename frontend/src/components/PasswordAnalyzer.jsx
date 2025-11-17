import React, { useState } from "react";
// L'importazione di BACKEND_URL è stata rimossa, in quanto usiamo il proxy Nginx.
// import { BACKEND_URL } from "../config"; 

// Nota: Ho aggiunto un po' di stile Tailwind per renderlo moderno e leggibile.
// Ho anche impostato 'credentials: 'include'' per inviare il cookie di sessione.

export default function PasswordAnalyzer() {
  const [password, setPassword] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // *** CORREZIONE: Uso del percorso relativo per il proxy Nginx ***
      // La richiesta sarà inoltrata al backend: 
      // /api/analyze-password -> https://password-backend-749522457256.us-central1.run.app/api/analyze-password
      const res = await fetch(`/api/analyze-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // IMPORTANTE: Inclusione del cookie di sessione per l'autorizzazione
        credentials: 'include', 
        body: JSON.stringify({ password }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Gestione di errori come 401 (Non autorizzato) o altri messaggi dal backend
        setError(data.message || "Analysis failed. You may need to log in again.");
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Network error. Could not reach the server.");
      console.error("Analysis Network Error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Funzione helper per lo stile
  const getStrengthColor = (level) => {
    if (level.includes("Strong") || level.includes("Excellent")) return "text-green-500 font-bold";
    if (level.includes("Fair")) return "text-yellow-500 font-bold";
    if (level.includes("Weak")) return "text-red-500 font-bold";
    return "text-gray-500";
  };

  return (
    <div className="p-6 max-w-lg mx-auto bg-white rounded-xl shadow-2xl space-y-6 m-8">
      <h2 className="text-2xl font-bold text-gray-800 border-b pb-2">Password Strength Analyzer</h2>
      
      <div className="space-y-4">
        <input
          type="password"
          placeholder="Enter password to analyze"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
          aria-label="Password Input"
        />
        <button 
          onClick={handleAnalyze} 
          disabled={loading || password.length === 0}
          className="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-md transition duration-150 ease-in-out disabled:opacity-50"
        >
          {loading ? "Analyzing…" : "Analyze Password"}
        </button>
      </div>

      {error && <p className="p-2 text-red-700 bg-red-100 rounded-lg text-sm">{error}</p>}

      {result && (
        <div className="pt-4 border-t mt-4 space-y-3">
          <p className="text-lg text-gray-700">
            Strength: <span className={getStrengthColor(result.level)}>{result.level}</span>
          </p>
          
          <h3 className="font-semibold text-gray-700">Suggestions to Improve:</h3>
          <ul className="list-disc list-inside ml-4 text-sm text-gray-600 space-y-1">
            {result.suggestions && result.suggestions.length > 0 ? (
              result.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))
            ) : (
                <li>Your password is strong!</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}