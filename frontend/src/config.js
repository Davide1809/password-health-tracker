// frontend/src/config.js (o dove hai definito BACKEND_URL)
export const BACKEND_URL =
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:5001"   // sviluppo locale
    : "http://backend:5001";     // dentro Docker (backend è il nome del servizio docker-compose)