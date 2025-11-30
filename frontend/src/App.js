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

  useEffect(() => {
    // Check if token exists and is valid
    const token = localStorage.getItem('token');
    setAuthToken(token);
    setIsLoading(false);
  }, []);

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  if (isLoading) {
    return <AppContainer>Loading...</AppContainer>;
  }

  return (
    <AppContainer>
      <Router>
        {authToken && <Navigation isAuthenticated={!!authToken} onLogout={handleLogout} />}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/"
            element={
              <ProtectedRoute isAuthenticated={!!authToken}>
                <Dashboard />
              </ProtectedRoute>
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
