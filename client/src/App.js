import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Signup from "./components/Signup";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<div>Welcome! Go to <a href="/signup">Signup</a></div>} />
        <Route path="/dashboard" element={<div>Dashboard (protected area)</div>} />
      </Routes>
    </Router>
  );
}

export default App;
