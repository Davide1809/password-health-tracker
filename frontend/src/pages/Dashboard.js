import React, { useEffect } from 'react';
import styled from 'styled-components';
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

function Dashboard() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userName = user.name || 'User';

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
    </Container>
  );
}

export default Dashboard;
