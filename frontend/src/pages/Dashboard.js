import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { getApiBase } from '../config';
import Credentials from '../components/Credentials';

const Container = styled.div`
  max-width: 1200px;
  margin: 2rem auto;
  padding: 2rem;
`;

const Card = styled.div`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  color: white;
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.5rem;
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
`;

const FeatureCard = styled(Card)`
  text-align: center;

  h3 {
    color: #667eea;
    margin-bottom: 1rem;
  }

  p {
    color: #666;
    line-height: 1.6;
  }
`;

const DangerZone = styled(Card)`
  border: 2px solid #ff4757;
  background: #fff5f5;

  h3 {
    color: #ff4757;
    margin-bottom: 1rem;
  }

  p {
    color: #666;
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }
`;

const DeleteButton = styled.button`
  background: #ff4757;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s ease;

  &:hover {
    background: #ff3838;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const Modal = styled.div`
  display: ${props => (props.isOpen ? 'flex' : 'none')};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);

  h2 {
    color: #ff4757;
    margin-bottom: 1rem;
  }

  p {
    color: #666;
    margin-bottom: 1rem;
    line-height: 1.6;
  }
`;

const ModalButtons = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s ease;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const CancelButton = styled(Button)`
  background: #e0e0e0;
  color: #333;

  &:hover:not(:disabled) {
    background: #d0d0d0;
  }
`;

const ConfirmDeleteButton = styled(Button)`
  background: #ff4757;
  color: white;

  &:hover:not(:disabled) {
    background: #ff3838;
  }
`;

const WarningText = styled.div`
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-weight: 500;
`;

function Dashboard() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userName = user.name || 'User';
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    // Handle page close/tab close - auto logout
    const handleBeforeUnload = () => {
      // Clear auth tokens and user data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const handleDeleteAccountClick = () => {
    setIsModalOpen(true);
    setError(null);
  };

  const handleCancelDelete = () => {
    setIsModalOpen(false);
    setError(null);
  };

  const handleConfirmDelete = async () => {
    try {
      setIsDeleting(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const apiBase = await getApiBase();
      const response = await axios.post(
        `${apiBase}/api/auth/delete-account`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      console.log('🗑️ Account deleted successfully:', response.data);
      
      // Clear auth data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      setSuccess('Account deleted successfully. Redirecting...');
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err) {
      console.error('🗑️ Delete account error:', err);
      setError(err.response?.data?.error || 'Failed to delete account. Please try again.');
      setIsDeleting(false);
    }
  };

  if (success) {
    return (
      <Container>
        <Card>
          <h2>✅ {success}</h2>
        </Card>
      </Container>
    );
  }

  return (
    <Container>
      <Title>Welcome, {userName}! 👋</Title>
      
      <Card>
        <h2>About This Application</h2>
        <p>
          Password Health Tracker helps you evaluate the strength and safety of your passwords. 
          Our application provides real-time password strength assessments, breach detection checks, 
          and AI-powered recommendations for creating stronger passwords.
        </p>
      </Card>

      <FeatureGrid>
        <FeatureCard>
          <h3>🔍 Strength Analysis</h3>
          <p>Real-time analysis of your password strength using advanced algorithms</p>
        </FeatureCard>

        <FeatureCard>
          <h3>🛡️ Breach Detection</h3>
          <p>Check if your password has appeared in known data breaches</p>
        </FeatureCard>

        <FeatureCard>
          <h3>🤖 AI Recommendations</h3>
          <p>Get intelligent suggestions to improve your password security</p>
        </FeatureCard>

        <FeatureCard>
          <h3>📊 Dashboard</h3>
          <p>Track your password health and improvement over time</p>
        </FeatureCard>

        <FeatureCard>
          <h3>🔐 Privacy First</h3>
          <p>Your passwords are never stored or transmitted insecurely</p>
        </FeatureCard>

        <FeatureCard>
          <h3>⚡ Instant Results</h3>
          <p>Get immediate feedback on password security</p>
        </FeatureCard>
      </FeatureGrid>

      <Card>
        <h2>Getting Started</h2>
        <p>
          To check your password strength, navigate to the "Checker" page and enter a password 
          you'd like to analyze. We'll provide a detailed report on its strength, security risks, 
          and recommendations for improvement.
        </p>
      </Card>

      <Credentials />

      <DangerZone>
        <h3>⚠️ Danger Zone</h3>
        <p>
          Deleting your account is permanent and cannot be undone. 
          This action will remove your account and all associated data from our system.
        </p>
        <DeleteButton onClick={handleDeleteAccountClick} disabled={isDeleting}>
          {isDeleting ? 'Deleting Account...' : 'Delete Account'}
        </DeleteButton>
      </DangerZone>

      <Modal isOpen={isModalOpen}>
        <ModalContent>
          <h2>🗑️ Delete Account</h2>
          <WarningText>
            ⚠️ WARNING: This action is permanent and cannot be undone!
          </WarningText>
          <p>
            Deleting your account will:
          </p>
          <ul style={{ color: '#666', marginBottom: '1rem' }}>
            <li>Remove your account from our system</li>
            <li>Delete all saved credentials and passwords</li>
            <li>Remove all your data</li>
            <li>Cannot be recovered</li>
          </ul>
          <p style={{ fontWeight: 'bold', color: '#ff4757' }}>
            Are you absolutely sure you want to delete your account?
          </p>
          {error && (
            <div style={{
              background: '#ffe0e0',
              color: '#ff4757',
              padding: '0.75rem',
              borderRadius: '4px',
              marginBottom: '1rem'
            }}>
              ❌ {error}
            </div>
          )}
          <ModalButtons>
            <CancelButton onClick={handleCancelDelete} disabled={isDeleting}>
              Cancel
            </CancelButton>
            <ConfirmDeleteButton onClick={handleConfirmDelete} disabled={isDeleting}>
              {isDeleting ? 'Deleting...' : 'Yes, Delete My Account'}
            </ConfirmDeleteButton>
          </ModalButtons>
        </ModalContent>
      </Modal>
    </Container>
  );
}

export default Dashboard;
