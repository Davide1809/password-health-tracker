import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled from 'styled-components';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import PasswordChecker from './pages/PasswordChecker';
import Results from './pages/Results';
import About from './pages/About';
import Login from './pages/Login';
import SignUp from './pages/SignUp';
import { getRuntimeConfig } from './config';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

// Protected route component
const ProtectedRoute = ({ isAuthenticated, children }) => {
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  const [authToken, setAuthToken] = useState(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);
  const [configLoaded, setConfigLoaded] = useState(false);

  useEffect(() => {
    // Preload runtime config before rendering anything
    getRuntimeConfig().then(() => {
      setConfigLoaded(true);
    }).catch(() => {
      setConfigLoaded(true); // Continue even if config fails
    });
  }, []);

  useEffect(() => {
    if (!configLoaded) return;

    // Check if token exists and is valid
    const token = localStorage.getItem('token');
    setAuthToken(token);
    setIsLoading(false);

    // Listen for storage changes (logout in other tabs, etc.)
    const handleStorageChange = () => {
      const newToken = localStorage.getItem('token');
      setAuthToken(newToken);
    };

    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [configLoaded]);

  const handleLogin = (token) => {
    localStorage.setItem('token', token);
    setAuthToken(token);
  };

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  if (isLoading || !configLoaded) {
    return <AppContainer>Loading...</AppContainer>;
  }

  return (
    <AppContainer>
      <Router>
        {authToken && <Navigation isAuthenticated={!!authToken} onLogout={handleLogout} />}
        <Routes>
          <Route path="/login" element={<Login onLoginSuccess={handleLogin} />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute isAuthenticated={!!authToken}>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              authToken ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/checker"
            element={
              <ProtectedRoute isAuthenticated={!!authToken}>
                <PasswordChecker />
              </ProtectedRoute>
            }
          />
          <Route
            path="/results"
            element={
              <ProtectedRoute isAuthenticated={!!authToken}>
                <Results />
              </ProtectedRoute>
            }
          />
          <Route path="/about" element={<About />} />
        </Routes>
      </Router>
    </AppContainer>
  );
}

export default App;
