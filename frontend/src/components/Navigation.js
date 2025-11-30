import React from 'react';
import styled from 'styled-components';
import { Link, useNavigate } from 'react-router-dom';

const Nav = styled.nav`
  background-color: rgba(0, 0, 0, 0.8);
  padding: 1rem 2rem;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.h1`
  font-size: 1.8rem;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;
  align-items: center;

  a {
    color: white;
    text-decoration: none;
    transition: color 0.3s;

    &:hover {
      color: #667eea;
    }
  }

  button {
    background-color: #764ba2;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;

    &:hover {
      background-color: #667eea;
    }
  }

  .auth-button {
    background-color: #667eea;
    padding: 0.5rem 1.2rem;
    border-radius: 6px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: background-color 0.3s ease;

    &:hover {
      background-color: #764ba2;
    }
  }
`;

function Navigation({ isAuthenticated, onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login', { replace: true });
  };

  return (
    <Nav>
      <Logo onClick={() => navigate(isAuthenticated ? '/dashboard' : '/about')}>
        🔐 Password Health Tracker
      </Logo>
      <NavLinks>
        {isAuthenticated && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/checker">Checker</Link>
            <Link to="/about">About</Link>
            <button onClick={handleLogout}>
              Logout
            </button>
          </>
        )}
        {!isAuthenticated && (
          <>
            <Link to="/about">About</Link>
            <button className="auth-button" onClick={() => navigate('/login')}>
              Sign In
            </button>
            <button className="auth-button" onClick={() => navigate('/signup')}>
              Sign Up
            </button>
          </>
        )}
      </NavLinks>
    </Nav>
  );
}

export default Navigation;
