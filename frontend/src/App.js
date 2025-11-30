import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import PasswordChecker from './pages/PasswordChecker';
import Results from './pages/Results';
import About from './pages/About';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('authToken'));

  const handleLogin = (token) => {
    setAuthToken(token);
    localStorage.setItem('authToken', token);
  };

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('authToken');
  };

  return (
    <AppContainer>
      <Router>
        <Navigation isAuthenticated={!!authToken} onLogout={handleLogout} />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/checker" element={<PasswordChecker />} />
          <Route path="/results" element={<Results />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Router>
    </AppContainer>
  );
}

export default App;
