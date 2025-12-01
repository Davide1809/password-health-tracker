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

const GenerateButton = styled(Button)`
  background: #06a77d;
  flex: 1;
  margin-bottom: 1rem;

  &:hover:not(:disabled) {
    background: #058b6f;
  }
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

const CodeBlock = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #2d3436;
  border-radius: 6px;
  margin-top: 0.75rem;
  border: 1px solid #636e72;

  code {
    font-family: 'Courier New', monospace;
    color: #00ff41;
    font-size: 1.1rem;
    word-break: break-all;
    flex: 1;
  }
`;

const CopyButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  white-space: nowrap;
  transition: background 0.3s;

  &:hover {
    background: #764ba2;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const WarningNote = styled.div`
  background: #fff3cd;
  border: 1px solid #ffc107;
  color: #856404;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const RecommendationsList = styled.ul`
  list-style: none;
  padding: 0;
  margin-top: 0.75rem;

  li {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    background: #f9f9f9;
    border-left: 3px solid #667eea;
    border-radius: 4px;
    color: #555;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;

    &:before {
      content: '✓';
      color: #667eea;
      font-weight: bold;
      flex-shrink: 0;
    }
  }
`;

const AttemptsNote = styled.div`
  background: #e3f2fd;
  border: 1px solid #2196f3;
  color: #1565c0;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-top: 0.75rem;
`;

function PasswordChecker() {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [suggestionsRemaining, setSuggestionsRemaining] = useState(3);
  const [copiedToClipboard, setCopiedToClipboard] = useState(false);
  const [generatingPassword, setGeneratingPassword] = useState(false);

  // Real-time password analysis as user types (auto-submit on each keystroke)
  const analyzePassword = async (pwd) => {
    if (!pwd || pwd.length < 3) {
      setResult(null);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const apiBase = await getApiBase();
      const response = await axios.post(
        `${apiBase}/api/passwords/analyze`,
        { password: pwd },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          },
          timeout: 5000
        }
      );
      setResult(response.data);
      setError('');
    } catch (err) {
      // Don't show error for real-time updates, only on explicit submit
      console.log('Real-time analysis error:', err.message);
    }
  };

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    // Real-time updates as user modifies password
    analyzePassword(newPassword);
  };

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

    setGeneratingPassword(true);
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
      setCopiedToClipboard(false);
    } catch (err) {
      setError('Failed to generate password. Please try again.');
    } finally {
      setGeneratingPassword(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedPassword);
    setCopiedToClipboard(true);
    setTimeout(() => setCopiedToClipboard(false), 2000);
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
            onChange={handlePasswordChange}
            placeholder="Enter password to check (real-time analysis)"
            disabled={loading}
          />
        </InputGroup>
        <Button type="submit" disabled={loading || !password}>
          {loading ? 'Analyzing...' : 'Full Analysis (Submit)'}
        </Button>
      </Form>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {result && (
        <ResultsDisplay 
          result={result} 
          onGeneratePassword={generateStrongPassword} 
          suggestionsRemaining={suggestionsRemaining}
          generatingPassword={generatingPassword}
        />
      )}

      {generatedPassword && (
        <ResultsCard>
          <h2>✅ Generated Strong Password</h2>
          <p style={{ marginBottom: '0.5rem' }}>
            <strong>Your Generated Password:</strong>
          </p>
          <CodeBlock>
            <code>{generatedPassword}</code>
            <CopyButton onClick={copyToClipboard}>
              {copiedToClipboard ? '✓ Copied!' : '📋 Copy'}
            </CopyButton>
          </CodeBlock>
          <WarningNote>
            <span>ℹ️</span>
            <span>This password is displayed but <strong>not saved</strong>. Copy it to your password manager or save it securely.</span>
          </WarningNote>
          <AttemptsNote>
            💡 Generation attempts remaining this session: <strong>{suggestionsRemaining}</strong>
          </AttemptsNote>
        </ResultsCard>
      )}
    </Container>
  );
}

function ResultsDisplay({ result, onGeneratePassword, suggestionsRemaining, generatingPassword }) {
  if (result.error) {
    return <ErrorMessage>{result.error}</ErrorMessage>;
  }

  return (
    <ResultsCard>
      <h2>📊 Analysis Results</h2>

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
            <p style={{ marginTop: '1rem', fontStyle: 'italic', color: '#666', backgroundColor: '#f5f5f5', padding: '0.75rem', borderRadius: '4px' }}>
              💡 <strong>Feedback:</strong> {result.strength.feedback}
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

      {/* Recommendations as bullet-point list */}
      {result.recommendations && Array.isArray(result.recommendations) && result.recommendations.length > 0 && (
        <div style={{ marginTop: '1.5rem' }}>
          <h3 style={{ color: '#333', marginBottom: '0.75rem' }}>💡 Recommendations</h3>
          <RecommendationsList>
            {result.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </RecommendationsList>
          <GenerateButton onClick={onGeneratePassword} disabled={suggestionsRemaining <= 0 || generatingPassword}>
            {generatingPassword ? '⏳ Generating...' : `🔄 Generate Strong Password (${suggestionsRemaining} attempts left)`}
          </GenerateButton>
        </div>
      )}
    </ResultsCard>
  );
}

export default PasswordChecker;
