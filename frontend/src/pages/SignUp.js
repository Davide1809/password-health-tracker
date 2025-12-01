import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getApiBase, getRuntimeConfig } from '../config';

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

  &:invalid:not(:placeholder-shown) {
    border-color: #ff6b6b;
  }
`;

const Select = styled.select`
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  background-color: white;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #667eea;
  }

  &:invalid:not(:placeholder-shown) {
    border-color: #ff6b6b;
  }
`;

const PasswordRequirements = styled.div`
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
`;

const Requirement = styled.p`
  display: flex;
  align-items: center;
  margin: 0.3rem 0;
  
  &::before {
    content: '${props => props.met ? '✓' : '○'}';
    margin-right: 0.5rem;
    color: ${props => props.met ? '#4CAF50' : '#ccc'};
    font-weight: bold;
  }
  
  color: ${props => props.met ? '#4CAF50' : '#666'};
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

  &:active {
    transform: translateY(0);
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

const SignUp = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    security_question_id: '',
    security_answer: ''
  });
  const [questions, setQuestions] = useState([]);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);

  // Ensure config is initialized when component mounts
  useEffect(() => {
    console.log('📝 SignUp component mounted, ensuring config is ready...');
    getRuntimeConfig().then(() => {
      console.log('📝 Config ready on SignUp component mount');
      fetchSecurityQuestions();
    }).catch((err) => {
      console.warn('📝 Config initialization error (will use fallback):', err);
    });
  }, []);

  // Fetch security questions
  const fetchSecurityQuestions = async () => {
    try {
      const apiBase = await getApiBase();
      const response = await axios.get(`${apiBase}/api/security-questions/questions`);
      setQuestions(response.data.questions || []);
      console.log('✅ Security questions loaded:', response.data.questions.length);
    } catch (error) {
      console.error('❌ Failed to load security questions:', error);
      setMessage({ type: 'warning', text: 'Could not load security questions' });
    }
  };

  // Password strength requirements
  const passwordRequirements = {
    length: formData.password.length >= 8,
    uppercase: /[A-Z]/.test(formData.password),
    lowercase: /[a-z]/.test(formData.password),
    number: /\d/.test(formData.password),
    special: /[!@#$%^&*()_+\-=[\]{};:'"<>?/\\|`~]/.test(formData.password)
  };

  const allRequirementsMet = Object.values(passwordRequirements).every(req => req);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field
    setErrors(prev => ({
      ...prev,
      [name]: ''
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    // Name validation
    if (!formData.name) {
      newErrors.name = 'Name is required';
    } else if (formData.name.length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!allRequirementsMet) {
      newErrors.password = 'Password does not meet all requirements';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Security question validation
    if (!formData.security_question_id) {
      newErrors.security_question_id = 'Please select a security question';
    }

    if (!formData.security_answer) {
      newErrors.security_answer = 'Security answer is required';
    } else if (formData.security_answer.length < 2) {
      newErrors.security_answer = 'Answer must be at least 2 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      console.log('📝 Getting API base for registration...');
      const apiBase = await getApiBase();
      console.log('📝 API base resolved to:', apiBase);
      
      console.log('📝 Sending registration request to:', `${apiBase}/api/auth/register`);
      await axios.post(
        `${apiBase}/api/auth/register`,
        {
          name: formData.name,
          email: formData.email,
          password: formData.password,
          security_question_id: parseInt(formData.security_question_id),
          security_answer: formData.security_answer
        }
      );

      console.log('📝 Registration successful');
      setMessage({
        type: 'success',
        text: 'Account created successfully! Redirecting to login...'
      });

      // Clear form
      setFormData({ 
        name: '', 
        email: '', 
        password: '', 
        confirmPassword: '',
        security_question_id: '',
        security_answer: ''
      });

      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      console.error('📝 Registration error:', error);
      const errorText = error.response?.data?.error || 'Registration failed. Please try again.';
      setMessage({
        type: 'error',
        text: errorText
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <FormContainer>
        <Title>Create Account</Title>
        <Subtitle>Join Password Health Tracker</Subtitle>

        {message.text && (
          message.type === 'error' ? (
            <ErrorMessage>{message.text}</ErrorMessage>
          ) : (
            <SuccessMessage>{message.text}</SuccessMessage>
          )
        )}

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="John Doe"
            />
            {errors.name && <ErrorMessage>{errors.name}</ErrorMessage>}
          </FormGroup>

          <FormGroup>
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
            />
            {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
          </FormGroup>

          <FormGroup>
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter password"
            />
            <PasswordRequirements>
              <Requirement met={passwordRequirements.length}>
                At least 8 characters
              </Requirement>
              <Requirement met={passwordRequirements.uppercase}>
                Contains uppercase letter (A-Z)
              </Requirement>
              <Requirement met={passwordRequirements.lowercase}>
                Contains lowercase letter (a-z)
              </Requirement>
              <Requirement met={passwordRequirements.number}>
                Contains number (0-9)
              </Requirement>
              <Requirement met={passwordRequirements.special}>
                Contains special character (!@#$%^&*...)
              </Requirement>
            </PasswordRequirements>
            {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
          </FormGroup>

          <FormGroup>
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input
              id="confirmPassword"
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm password"
            />
            {errors.confirmPassword && (
              <ErrorMessage>{errors.confirmPassword}</ErrorMessage>
            )}
          </FormGroup>

          <FormGroup>
            <Label htmlFor="security_question_id">🔐 Security Question (for account recovery)</Label>
            <Select
              id="security_question_id"
              name="security_question_id"
              value={formData.security_question_id}
              onChange={handleChange}
            >
              <option value="">-- Select a security question --</option>
              {questions.map(q => (
                <option key={q.id} value={q.id}>{q.question}</option>
              ))}
            </Select>
            {errors.security_question_id && (
              <ErrorMessage>{errors.security_question_id}</ErrorMessage>
            )}
          </FormGroup>

          <FormGroup>
            <Label htmlFor="security_answer">Answer to Security Question</Label>
            <Input
              id="security_answer"
              type="text"
              name="security_answer"
              value={formData.security_answer}
              onChange={handleChange}
              placeholder="Your answer"
            />
            {errors.security_answer && (
              <ErrorMessage>{errors.security_answer}</ErrorMessage>
            )}
          </FormGroup>

          <Button type="submit" disabled={loading || !allRequirementsMet}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </Form>

        <LoginLink>
          Already have an account?{' '}
          <a href="#login" onClick={(e) => { e.preventDefault(); navigate('/login'); }}>Sign In</a>
        </LoginLink>
      </FormContainer>
    </Container>
  );
};

export default SignUp;
