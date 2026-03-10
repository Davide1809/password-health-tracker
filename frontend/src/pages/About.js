import React from 'react';
import styled from 'styled-components';

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
  line-height: 1.8;

  h2 {
    color: #333;
    margin-bottom: 1rem;
  }

  h3 {
    color: #667eea;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
  }

  p {
    color: #666;
    margin-bottom: 1rem;
  }

  ul {
    margin-left: 1.5rem;
    margin-bottom: 1rem;

    li {
      margin-bottom: 0.5rem;
      color: #666;
    }
  }
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
    margin-top: 0;
  }

  p {
    color: #666;
    line-height: 1.6;
  }
`;

function About() {
  return (
    <Container>
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

      <Card>
        <h2>Why Password Security Matters</h2>
        <p>
          The Password Health Tracker is a web-based application designed to help users evaluate 
          the strength and safety of their passwords. With the alarming rate at which data breaches 
          occur, it's more important than ever to ensure your passwords are secure and unique.
        </p>
        <p>
          Too many people are using weak or compromised passwords, repeatedly leaving their personal 
          and professional accounts vulnerable to being hacked. Our application fixes that by providing:
        </p>
        <ul>
          <li>Real-time password strength assessments</li>
          <li>Breach detection using the "Have I Been Pwned" API</li>
          <li>AI-generated recommendations for stronger passwords</li>
          <li>A user-friendly dashboard for tracking results</li>
        </ul>

        <h3>Who Should Use This?</h3>
        <p>
          This application is designed for students, employees in the workforce, and small business 
          owners looking for private, trusted tools to assess password safety and strength. We believe 
          that everyone deserves to understand their password security and adopt better password practices.
        </p>
      </Card>

      <Card>
        <h2>Technology Stack</h2>
        <ul>
          <li><strong>Backend:</strong> Python (Flask)</li>
          <li><strong>Frontend:</strong> React</li>
          <li><strong>Database:</strong> MongoDB</li>
          <li><strong>Containerization:</strong> Docker</li>
          <li><strong>Deployment:</strong> Google Cloud Platform</li>
          <li><strong>CI/CD:</strong> GitHub Actions</li>
          <li><strong>AI Integration:</strong> OpenAI API, ChatGPT</li>
        </ul>

        <h3>Core Features</h3>
        <ul>
          <li>Password strength scoring using advanced algorithms</li>
          <li>Breach detection against known compromised passwords</li>
          <li>AI-powered recommendations to improve password strength</li>
          <li>User-friendly dashboard displaying analysis results</li>
          <li>Privacy-first approach - passwords are never stored</li>
        </ul>

        <h3>Privacy & Security</h3>
        <p>
          Your privacy and security are our top priorities. We use end-to-end encryption for all 
          data transmission, never store your passwords, and follow industry best practices for 
          data protection.
        </p>
      </Card>

      <Card>
        <h2>Contact & Support</h2>
        <p>
          For questions, feedback, or support, please reach out to us through our GitHub repository 
          or contact us directly at support@passwordhealthtracker.com
        </p>
      </Card>
    </Container>
  );
}

export default About;
