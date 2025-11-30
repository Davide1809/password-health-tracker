import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 900px;
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

function About() {
  return (
    <Container>
      <Card>
        <h2>About Password Health Tracker</h2>
        <p>
          The Password Health Tracker is a web-based application designed to help users evaluate 
          the strength and safety of their passwords. With the alarming rate at which data breaches 
          occur, it's more important than ever to ensure your passwords are secure and unique.
        </p>

        <h3>Why Password Security Matters</h3>
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

        <h3>Technology Stack</h3>
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
