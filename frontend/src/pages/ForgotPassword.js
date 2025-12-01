import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { getApiBase } from '../config';

const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const FormContainer = styled.div`
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 420px;
`;

const Title = styled.h1`
  margin-bottom: 0.5rem;
  font-size: 2rem;
  color: #333;
  text-align: center;
`;

const Subtitle = styled.p`
  margin-bottom: 2rem;
  color: #666;
  text-align: center;
  font-size: 0.95rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  color: #333;
  font-weight: 600;
  font-size: 0.95rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const QuestionDisplay = styled.div`
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #667eea;
  margin-bottom: 1rem;
  font-weight: 500;
  color: #333;
`;

const Button = styled.button`
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  background-color: #ffebee;
  color: #c62828;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  border-left: 4px solid #c62828;
`;

const SuccessMessage = styled.div`
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  border-left: 4px solid #2e7d32;
`;

const LoginLink = styled.p`
  text-align: center;
  margin-top: 1.5rem;
  color: #666;

  a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    cursor: pointer;

    &:hover {
      text-decoration: underline;
    }
  }
`;

function ForgotPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState('email'); // 'email', 'security', or 'reset'
  const [email, setEmail] = useState('');
  const [securityAnswer, setSecurityAnswer] = useState('');
  const [securityQuestion, setSecurityQuestion] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);
  const [securityToken, setSecurityToken] = useState('');
  const resetToken = searchParams.get('token');

  // If reset token exists in URL, skip to reset step
  React.useEffect(() => {
    if (resetToken) {
      setStep('reset');
    }
  }, [resetToken]);

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setErrors({});

    if (!email) {
      setErrors({ email: 'Email is required' });
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setErrors({ email: 'Please enter a valid email' });
      return;
    }

    setLoading(true);
    try {
      const apiBase = await getApiBase();
      // First, verify the email exists
      await axios.post(
        `${apiBase}/api/auth/forgot-password`,
        { email }
      );

      // Fetch the user's security question
      const questionResponse = await axios.post(
        `${apiBase}/api/security-questions/get-question-for-email`,
        { email }
      );

      // Store the question for display
      setSecurityQuestion(questionResponse.data.question);

      setMessage({
        type: 'success',
        text: 'Email verified! Now answer your security question.'
      });
      
      // Move to security question verification step
      setStep('security');
    } catch (error) {
      const errorText = error.response?.data?.error || 'Failed to verify email';
      setMessage({ type: 'error', text: errorText });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifySecurityAnswer = async (e) => {
    e.preventDefault();
    setErrors({});

    if (!securityAnswer) {
      setErrors({ securityAnswer: 'Security answer is required' });
      return;
    }

    setLoading(true);
    try {
      const apiBase = await getApiBase();
      const securityTokenResponse = await axios.post(
        `${apiBase}/api/auth/verify-security-answer`,
        {
          email: email,
          security_answer: securityAnswer
        }
      );

      // Store security token for password reset
      setSecurityToken(securityTokenResponse.data.security_token);
      
      setMessage({
        type: 'success',
        text: 'Security answer verified! Now create your new password.'
      });
      
      // Move to password reset step
      setStep('reset');
    } catch (error) {
      const errorText = error.response?.data?.error || 'Failed to verify security answer';
      setMessage({ type: 'error', text: errorText });
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setErrors({});

    const newErrors = {};

    if (!newPassword) {
      newErrors.newPassword = 'New password is required';
    } else if (newPassword.length < 8) {
      newErrors.newPassword = 'Password must be at least 8 characters';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    try {
      const apiBase = await getApiBase();
      
      // Use either the security token or the URL reset token
      const token = securityToken || resetToken;
      
      await axios.post(
        `${apiBase}/api/auth/reset-password`,
        {
          token: token,
          new_password: newPassword,
          confirm_password: confirmPassword
        }
      );

      setMessage({
        type: 'success',
        text: 'Password reset successful! Redirecting to login...'
      });

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      const errorText = error.response?.data?.error || 'Failed to reset password';
      setMessage({ type: 'error', text: errorText });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <FormContainer>
        <Title>🔐 Reset Password</Title>
        <Subtitle>
          {step === 'email' && 'Enter your email to get started'}
          {step === 'security' && 'Answer your security question'}
          {step === 'reset' && 'Create a new password'}
        </Subtitle>

        {message.text && (
          message.type === 'error' ? (
            <ErrorMessage>{message.text}</ErrorMessage>
          ) : (
            <SuccessMessage>{message.text}</SuccessMessage>
          )
        )}

        {step === 'email' && (
          <Form onSubmit={handleRequestReset}>
            <FormGroup>
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                disabled={loading}
              />
              {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
            </FormGroup>

            <Button type="submit" disabled={loading}>
              {loading ? 'Verifying...' : 'Verify Email'}
            </Button>
          </Form>
        )}

        {step === 'security' && (
          <Form onSubmit={handleVerifySecurityAnswer}>
            <FormGroup>
              <Label>Please answer your security question:</Label>
              <QuestionDisplay>
                🔐 {securityQuestion || 'Answer the security question you provided during account signup'}
              </QuestionDisplay>
              <Label htmlFor="securityAnswer">Your Answer</Label>
              <Input
                id="securityAnswer"
                type="text"
                value={securityAnswer}
                onChange={(e) => setSecurityAnswer(e.target.value)}
                placeholder="Your security answer"
                disabled={loading}
              />
              {errors.securityAnswer && <ErrorMessage>{errors.securityAnswer}</ErrorMessage>}
            </FormGroup>

            <Button type="submit" disabled={loading}>
              {loading ? 'Verifying...' : 'Verify Answer'}
            </Button>
          </Form>
        )}

        {step === 'reset' && (
          <Form onSubmit={handleResetPassword}>
            <FormGroup>
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                disabled={loading}
              />
              {errors.newPassword && <ErrorMessage>{errors.newPassword}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                disabled={loading}
              />
              {errors.confirmPassword && <ErrorMessage>{errors.confirmPassword}</ErrorMessage>}
            </FormGroup>

            <Button type="submit" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </Form>
        )}

        <LoginLink>
          Remember your password?{' '}
          <a href="#login" onClick={(e) => { e.preventDefault(); navigate('/login'); }}>
            Sign In
          </a>
        </LoginLink>
      </FormContainer>
    </Container>
  );
}

export default ForgotPassword;
