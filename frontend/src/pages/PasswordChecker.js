import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

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

function PasswordChecker() {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/passwords/analyze', {
        password: password
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error analyzing password:', error);
      setResult({
        error: 'Failed to analyze password. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Title>Check Your Password Strength</Title>
      <Form onSubmit={handleSubmit}>
        <InputGroup>
          <Label htmlFor="password">Enter Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password to check"
            required
          />
        </InputGroup>
        <Button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Password'}
        </Button>
      </Form>

      {result && (
        <ResultsDisplay result={result} />
      )}
    </Container>
  );
}

function ResultsDisplay({ result }) {
  if (result.error) {
    return <ErrorMessage>{result.error}</ErrorMessage>;
  }

  const ErrorMessage = styled.div`
    margin-top: 2rem;
    padding: 1rem;
    background-color: #ffebee;
    color: #c62828;
    border-radius: 4px;
  `;

  const StrengthBar = styled.div`
    margin-top: 1rem;
    height: 10px;
    background-color: #ddd;
    border-radius: 4px;
    overflow: hidden;

    div {
      height: 100%;
      background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcf7f);
      width: ${(props) => props.width}%;
      transition: width 0.3s;
    }
  `;

  return (
    <div style={{ marginTop: '2rem' }}>
      <h2>Analysis Results</h2>
      {result.strength && (
        <>
          <p><strong>Strength:</strong> {result.strength.strength}</p>
          <p><strong>Score:</strong> {result.strength.score}/4</p>
          <StrengthBar width={(result.strength.score / 4) * 100} />
          <p><strong>Entropy:</strong> {result.strength.entropy} bits</p>
        </>
      )}
      {result.breached !== undefined && (
        <p><strong>Breached:</strong> {result.breached ? 'Yes ⚠️' : 'No ✓'}</p>
      )}
    </div>
  );
}

export default PasswordChecker;
