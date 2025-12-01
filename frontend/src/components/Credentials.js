import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { getApiBase } from '../config';

const CredentialsContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  color: #333;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
`;

const FormSection = styled.div`
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 6px;
  margin-bottom: 2rem;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
`;

const Input = styled.input`
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const TextArea = styled.textarea`
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
`;

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  background: ${props => props.danger ? '#ff6b6b' : '#667eea'};
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px ${props => props.danger ? 'rgba(255, 107, 107, 0.4)' : 'rgba(102, 126, 234, 0.4)'};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const CredentialsList = styled.div`
  display: grid;
  gap: 1rem;
`;

const CredentialCard = styled.div`
  background: #f9f9f9;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  padding: 1.5rem;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  }
`;

const CredentialHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
`;

const WebsiteName = styled.h3`
  color: #667eea;
  margin: 0;
  font-size: 1.2rem;
`;

const CredentialField = styled.div`
  margin: 0.75rem 0;
`;

const FieldLabel = styled.span`
  color: #666;
  font-weight: 600;
  font-size: 0.9rem;
`;

const FieldValue = styled.span`
  color: #333;
  margin-left: 0.5rem;
  font-family: 'Courier New', monospace;
`;

const PasswordField = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const HiddenPassword = styled.span`
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
`;

const ShowButton = styled.button`
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-weight: 600;
  padding: 0;
  font-size: 0.85rem;

  &:hover {
    text-decoration: underline;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
`;

const EditButton = styled(Button)`
  background: #764ba2;
`;

const ErrorMessage = styled.div`
  background-color: #ffebee;
  color: #c62828;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  border-left: 4px solid #c62828;
  margin-bottom: 1rem;
`;

const SuccessMessage = styled.div`
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  border-left: 4px solid #2e7d32;
  margin-bottom: 1rem;
`;

function Credentials() {
  const [credentials, setCredentials] = useState([]);
  const [formData, setFormData] = useState({
    website_name: '',
    username: '',
    password: '',
    notes: ''
  });
  const [showPasswords, setShowPasswords] = useState({});
  const [message, setMessage] = useState({ type: '', text: '' });
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');

  // Fetch credentials on mount
  useEffect(() => {
    fetchCredentials();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const fetchCredentials = async () => {
    try {
      const apiBase = await getApiBase();
      const response = await axios.get(
        `${apiBase}/api/credentials`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setCredentials(response.data.credentials);
    } catch (error) {
      console.error('Failed to fetch credentials:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.website_name || !formData.username || !formData.password) {
      setMessage({ type: 'error', text: 'Website name, username, and password are required' });
      return;
    }

    setLoading(true);
    try {
      const apiBase = await getApiBase();
      await axios.post(
        `${apiBase}/api/credentials`,
        formData,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setMessage({ type: 'success', text: 'Credential added successfully!' });
      setFormData({ website_name: '', username: '', password: '', notes: '' });
      fetchCredentials();
    } catch (error) {
      const errorText = error.response?.data?.error || 'Failed to add credential';
      setMessage({ type: 'error', text: errorText });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (credentialId) => {
    if (!window.confirm('Are you sure you want to delete this credential?')) {
      return;
    }

    try {
      const apiBase = await getApiBase();
      await axios.delete(
        `${apiBase}/api/credentials/${credentialId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setMessage({ type: 'success', text: 'Credential deleted successfully!' });
      fetchCredentials();
    } catch (error) {
      const errorText = error.response?.data?.error || 'Failed to delete credential';
      setMessage({ type: 'error', text: errorText });
    }
  };

  const togglePasswordVisibility = (credentialId) => {
    setShowPasswords(prev => ({
      ...prev,
      [credentialId]: !prev[credentialId]
    }));
  };

  return (
    <CredentialsContainer>
      <Title>🔐 Saved Credentials</Title>

      {message.text && (
        message.type === 'error' ? (
          <ErrorMessage>{message.text}</ErrorMessage>
        ) : (
          <SuccessMessage>{message.text}</SuccessMessage>
        )
      )}

      <FormSection>
        <h3 style={{ marginTop: 0, color: '#333' }}>Add New Credential</h3>
        <form onSubmit={handleSubmit}>
          <FormGrid>
            <FormGroup>
              <Label htmlFor="website_name">Website Name</Label>
              <Input
                id="website_name"
                name="website_name"
                type="text"
                placeholder="e.g., Gmail, GitHub"
                value={formData.website_name}
                onChange={handleChange}
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="username">Username/Email</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="your.email@example.com"
                value={formData.username}
                onChange={handleChange}
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="Enter password"
                value={formData.password}
                onChange={handleChange}
              />
            </FormGroup>
          </FormGrid>

          <FormGroup>
            <Label htmlFor="notes">Notes (Optional)</Label>
            <TextArea
              id="notes"
              name="notes"
              placeholder="Add any notes about this credential..."
              value={formData.notes}
              onChange={handleChange}
              rows="3"
            />
          </FormGroup>

          <ButtonGroup>
            <Button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Credential'}
            </Button>
          </ButtonGroup>
        </form>
      </FormSection>

      <h3 style={{ color: '#333', marginBottom: '1rem' }}>
        Your Credentials ({credentials.length})
      </h3>

      {credentials.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#999' }}>
          <p>No credentials saved yet. Add one above to get started!</p>
        </div>
      ) : (
        <CredentialsList>
          {credentials.map(credential => (
            <CredentialCard key={credential.id}>
              <CredentialHeader>
                <WebsiteName>{credential.website_name}</WebsiteName>
              </CredentialHeader>

              <CredentialField>
                <FieldLabel>Username/Email:</FieldLabel>
                <FieldValue>{credential.username}</FieldValue>
              </CredentialField>

              <CredentialField>
                <FieldLabel>Password:</FieldLabel>
                <PasswordField>
                  {showPasswords[credential.id] ? (
                    <FieldValue>{credential.password}</FieldValue>
                  ) : (
                    <HiddenPassword>••••••••</HiddenPassword>
                  )}
                  <ShowButton onClick={() => togglePasswordVisibility(credential.id)}>
                    {showPasswords[credential.id] ? 'Hide' : 'Show'}
                  </ShowButton>
                </PasswordField>
              </CredentialField>

              {credential.notes && (
                <CredentialField>
                  <FieldLabel>Notes:</FieldLabel>
                  <FieldValue style={{ fontFamily: 'inherit' }}>{credential.notes}</FieldValue>
                </CredentialField>
              )}

              <ActionButtons>
                <DeleteButton onClick={() => handleDelete(credential.id)}>
                  Delete
                </DeleteButton>
              </ActionButtons>
            </CredentialCard>
          ))}
        </CredentialsList>
      )}
    </CredentialsContainer>
  );
}

export default Credentials;
