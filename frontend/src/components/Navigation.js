import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';

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
`;

function Navigation({ isAuthenticated, onLogout }) {
  return (
    <Nav>
      <Logo>🔐 Password Health Tracker</Logo>
      <NavLinks>
        <Link to="/">Home</Link>
        <Link to="/checker">Checker</Link>
        <Link to="/about">About</Link>
        {isAuthenticated && (
          <button onClick={onLogout}>Logout</button>
        )}
      </NavLinks>
    </Nav>
  );
}

export default Navigation;
