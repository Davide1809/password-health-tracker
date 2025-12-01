import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { getApiBase } from '../config';

const Container = styled.div`
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  color: #333;
  margin-bottom: 2rem;
  text-align: center;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  color: #555;
  font-weight: bold;
  margin-bottom: 0.5rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  margin-top: 2rem;
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  border-left: 4px solid #c62828;
`;



const StrengthBar = styled.div`
  margin-top: 1rem;
  height: 10px;
  background-color: #ddd;
  border-radius: 4px;
  overflow: hidden;

  div {
    height: 100%;
    background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
    width: ${(props) => props.width}%;
    transition: width 0.3s;
  }
`;

const ResultsCard = styled.div`
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #667eea;

  h2 {
    margin-top: 0;
    color: #333;
  }

  p {
    margin: 0.75rem 0;
    color: #555;
  }

  strong {
    color: #333;
  }
`;

const ScoreLabel = styled.span`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  margin-left: 0.5rem;

  background-color: ${(props) => {
    if (props.score >= 3) return '#4CAF50';
    if (props.score >= 2) return '#FFC107';
    return '#FF6B6B';
  }};
  color: white;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const SecondaryButton = styled(Button)`
  background: #764ba2;
  flex: 1;
`;

const BreachAlert = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  border-left: 4px solid #c62828;
`;

const BreachSafe = styled.div`
  margin-top: 1rem;
  padding: 1rem;
  background-color: #e8f5e9;
  color: #2e7d32;
  border-radius: 4px;
  border-left: 4px solid #2e7d32;
`;

function PasswordChecker() {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [suggestionsRemaining, setSuggestionsRemaining] = useState(3);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    setGeneratedPassword('');

    if (!password) {
      setError('Please enter a password');
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const apiBase = await getApiBase();
      const response = await axios.post(
        `${apiBase}/api/passwords/analyze`,
        { password },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      setResult(response.data);
    } catch (err) {
      const errorText = err.response?.data?.error || 'Failed to analyze password. Please try again.';
      setError(errorText);
    } finally {
      setLoading(false);
    }
  };

  const generateStrongPassword = async () => {
    if (suggestionsRemaining <= 0) {
      setError('Maximum suggestions reached. Refresh page to reset limit.');
      return;
    }

    try {
      const apiBase = await getApiBase();
      const response = await axios.post(
        `${apiBase}/api/ai/generate`,
        {
          length: 16,
          use_special: true,
          use_numbers: true
        }
      );
      setGeneratedPassword(response.data.generated_password);
      setSuggestionsRemaining(response.data.attempts_remaining);
    } catch (err) {
      setError('Failed to generate password');
    }
  };

  return (
    <Container>
      <Title>🔍 Check Your Password Strength</Title>
      <Form onSubmit={handleSubmit}>
        <InputGroup>
          <Label htmlFor="password">Enter Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password to check"
            disabled={loading}
          />
        </InputGroup>
        <Button type="submit" disabled={loading || !password}>
          {loading ? 'Analyzing...' : 'Analyze Password'}
        </Button>
      </Form>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {result && (
        <ResultsDisplay result={result} onGeneratePassword={generateStrongPassword} suggestionsRemaining={suggestionsRemaining} />
      )}

      {generatedPassword && (
        <ResultsCard>
          <h2>✅ Generated Strong Password</h2>
          <p style={{ marginBottom: '1rem' }}>
            <strong>Password:</strong>
            <code style={{ display: 'block', padding: '0.5rem', backgroundColor: '#f5f5f5', borderRadius: '4px', marginTop: '0.5rem', wordBreak: 'break-all' }}>
              {generatedPassword}
            </code>
          </p>
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            This password is displayed but not saved. Copy it to a secure location or password manager.
          </p>
          <p style={{ color: '#999', fontSize: '0.85rem' }}>
            Suggestions remaining this session: {suggestionsRemaining}
          </p>
        </ResultsCard>
      )}
    </Container>
  );
}

function ResultsDisplay({ result, onGeneratePassword, suggestionsRemaining }) {
  if (result.error) {
    return <ErrorMessage>{result.error}</ErrorMessage>;
  }

  return (
    <ResultsCard>
      <h2>Analysis Results</h2>

      {result.strength && (
        <>
          <p>
            <strong>Strength:</strong>
            <ScoreLabel score={result.strength.score}>
              {result.strength.strength}
            </ScoreLabel>
          </p>
          <p>
            <strong>Score:</strong> {result.strength.score}/4
          </p>
          <StrengthBar width={(result.strength.score / 4) * 100} />

          <p style={{ marginTop: '1rem' }}>
            <strong>Entropy:</strong> {result.strength.entropy?.toFixed(2) || 'N/A'} bits
          </p>

          {result.strength.feedback && (
            <p style={{ marginTop: '1rem', fontStyle: 'italic', color: '#666' }}>
              <strong>Feedback:</strong> {result.strength.feedback}
            </p>
          )}
        </>
      )}

      {/* Breach Status */}
      {result.breached !== undefined && (
        <>
          {result.breached ? (
            <BreachAlert>
              <strong>⚠️ Warning: Password Found in Data Breaches!</strong>
              <p>This password has been seen {result.breach_count} times in known data breaches.</p>
              <p>You should change this password immediately on all accounts where it's used.</p>
            </BreachAlert>
          ) : (
            <BreachSafe>
              <strong>✓ Safe: Not Found in Known Breaches</strong>
              <p>This password has not been detected in any known data breaches.</p>
            </BreachSafe>
          )}
        </>
      )}

      {result.recommendations && Array.isArray(result.recommendations) && (
        <div style={{ marginTop: '1.5rem' }}>
          <strong>Recommendations:</strong>
          <ul style={{ marginTop: '0.5rem' }}>
            {result.recommendations.map((rec, idx) => (
              <li key={idx} style={{ marginBottom: '0.5rem' }}>{rec}</li>
            ))}
          </ul>
          <ButtonGroup>
            <SecondaryButton onClick={onGeneratePassword} disabled={suggestionsRemaining <= 0}>
              🔄 Generate Strong Password ({suggestionsRemaining} left)
            </SecondaryButton>
          </ButtonGroup>
        </div>
      )}
    </ResultsCard>
  );
}

export default PasswordChecker;
