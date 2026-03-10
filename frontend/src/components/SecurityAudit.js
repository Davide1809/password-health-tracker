import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { getApiBase } from '../config';

const AuditContainer = styled.div`
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

const Button = styled.button`
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
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

const LoadingMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1.1rem;
`;

const ErrorMessage = styled.div`
  background-color: #ffebee;
  color: #c62828;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #c62828;
  margin-bottom: 1rem;
`;

const SuccessMessage = styled.div`
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #2e7d32;
  margin-bottom: 1rem;
`;

const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const SummaryCard = styled.div`
  background: linear-gradient(135deg, ${props => props.gradient} 0%, ${props => props.gradient2} 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;

  h3 {
    margin: 0;
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  p {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0.9;
  }
`;

const SecurityScoreCard = styled(SummaryCard)`
  grid-column: ${props => props.full ? 'span 1' : 'auto'};

  .score-circle {
    font-size: 3rem;
    font-weight: bold;
    margin: 0.5rem 0;
  }
`;

const IssueSection = styled.div`
  margin-bottom: 2rem;
`;

const IssueTitle = styled.h3`
  color: ${props => props.color || '#333'};
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;

  span {
    background: ${props => props.badgeColor || '#667eea'};
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
  }
`;

const IssueList = styled.div`
  display: grid;
  gap: 1rem;
`;

const IssueCard = styled.div`
  background: #f9f9f9;
  border: 2px solid ${props => props.borderColor || '#e0e0e0'};
  border-left: 4px solid ${props => props.borderColor || '#e0e0e0'};
  padding: 1rem;
  border-radius: 6px;

  h4 {
    margin: 0 0 0.5rem 0;
    color: #333;
  }

  p {
    margin: 0.5rem 0;
    color: #666;
    font-size: 0.9rem;
  }
`;

const DuplicateGroup = styled.div`
  background: #f9f9f9;
  border: 2px solid #ff9800;
  border-left: 4px solid #ff9800;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;

  h4 {
    margin: 0 0 0.5rem 0;
    color: #333;
  }
`;

const CredentialItem = styled.div`
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  margin: 0.5rem 0;
  font-size: 0.85rem;
  color: #666;

  strong {
    color: #333;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 2rem;
  color: #999;

  p {
    margin: 0;
    font-size: 1rem;
  }
`;

function SecurityAudit({ refetchTrigger = 0 }) {
  const [auditReport, setAuditReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const token = localStorage.getItem('token');

  const handleRunAudit = async () => {
    setLoading(true);
    setError(null);
    setAuditReport(null);

    try {
      const apiBase = await getApiBase();
      const response = await axios.post(
        `${apiBase}/api/audit/scan`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setAuditReport(response.data.audit_report);
    } catch (err) {
      console.error('Audit error:', err);
      setError(err.response?.data?.error || 'Failed to run security audit');
    } finally {
      setLoading(false);
    }
  };

  // Auto-run audit when refetchTrigger changes
  useEffect(() => {
    if (refetchTrigger > 0) {
      handleRunAudit();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refetchTrigger]);

  return (
    <AuditContainer>
      <Title>🔐 Security Audit</Title>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {loading && (
        <LoadingMessage>
          🔍 Scanning your credentials for security issues...
        </LoadingMessage>
      )}

      {!auditReport && !loading && (
        <div>
          <p style={{ color: '#666', marginBottom: '1.5rem' }}>
            Run a comprehensive security audit to identify weak passwords, breached credentials, and duplicate passwords across all your saved accounts.
          </p>
          <Button onClick={handleRunAudit} disabled={loading}>
            🔍 Run Security Audit
          </Button>
        </div>
      )}

      {auditReport && (
        <>
          <SuccessMessage>
            ✅ Security audit completed successfully!
          </SuccessMessage>

          {/* Summary Cards */}
          <SummaryGrid>
            <SecurityScoreCard gradient="#4caf50" gradient2="#8bc34a" full>
              <div className="score-circle">{auditReport.summary.security_score}</div>
              <h3>Security Score</h3>
              <p>Out of 100</p>
            </SecurityScoreCard>

            <SummaryCard gradient="#667eea" gradient2="#8bc34a">
              <h3>{auditReport.summary.total}</h3>
              <p>Total Credentials</p>
            </SummaryCard>

            <SummaryCard gradient="#4caf50" gradient2="#81c784">
              <h3>{auditReport.summary.strong}</h3>
              <p>Strong Passwords</p>
            </SummaryCard>

            <SummaryCard gradient="#ff9800" gradient2="#ffb74d">
              <h3>{auditReport.summary.weak}</h3>
              <p>Weak Passwords</p>
            </SummaryCard>

            <SummaryCard gradient="#f44336" gradient2="#ef5350">
              <h3>{auditReport.summary.breached}</h3>
              <p>Breached Passwords</p>
            </SummaryCard>

            <SummaryCard gradient="#9c27b0" gradient2="#ba68c8">
              <h3>{auditReport.summary.duplicates}</h3>
              <p>Reused Passwords</p>
            </SummaryCard>
          </SummaryGrid>

          {/* Weak Passwords */}
          {auditReport.weak_passwords.length > 0 && (
            <IssueSection>
              <IssueTitle color="#ff9800" badgeColor="#ff9800">
                ⚠️ Weak Passwords <span>{auditReport.weak_passwords.length}</span>
              </IssueTitle>
              <IssueList>
                {auditReport.weak_passwords.map((cred, idx) => (
                  <IssueCard key={idx} borderColor="#ff9800">
                    <h4>📱 {cred.website}</h4>
                    <p>
                      <strong>Username:</strong> {cred.username}
                    </p>
                    <p>
                      <strong>Strength:</strong> {cred.strength} (Score: {cred.score}/100)
                    </p>
                    {cred.feedback && cred.feedback.length > 0 && (
                      <p>
                        <strong>Recommendations:</strong>
                        <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }}>
                          {cred.feedback.map((tip, i) => (
                            <li key={i}>{tip}</li>
                          ))}
                        </ul>
                      </p>
                    )}
                  </IssueCard>
                ))}
              </IssueList>
            </IssueSection>
          )}

          {/* Breached Passwords */}
          {auditReport.breached_passwords.length > 0 && (
            <IssueSection>
              <IssueTitle color="#f44336" badgeColor="#f44336">
                🚨 Breached Passwords <span>{auditReport.breached_passwords.length}</span>
              </IssueTitle>
              <IssueList>
                {auditReport.breached_passwords.map((cred, idx) => (
                  <IssueCard key={idx} borderColor="#f44336">
                    <h4>📱 {cred.website}</h4>
                    <p>
                      <strong>Username:</strong> {cred.username}
                    </p>
                    <p style={{ color: '#f44336', fontWeight: 'bold' }}>
                      ⚠️ This password has been found in {cred.breach_count} data breaches
                    </p>
                    <p style={{ marginTop: '0.5rem', color: '#666' }}>
                      <strong>Action:</strong> Change this password immediately on {cred.website}
                    </p>
                  </IssueCard>
                ))}
              </IssueList>
            </IssueSection>
          )}

          {/* Duplicate Passwords */}
          {auditReport.duplicate_passwords.length > 0 && (
            <IssueSection>
              <IssueTitle color="#9c27b0" badgeColor="#9c27b0">
                🔄 Reused Passwords <span>{auditReport.duplicate_passwords.length}</span>
              </IssueTitle>
              <div>
                {auditReport.duplicate_passwords.map((group, idx) => (
                  <DuplicateGroup key={idx}>
                    <h4>📋 Used on {group.count} accounts</h4>
                    <p style={{ color: '#666', marginBottom: '0.5rem' }}>
                      Using the same password across multiple accounts increases your risk. Consider using unique passwords.
                    </p>
                    {group.credentials.map((cred, i) => (
                      <CredentialItem key={i}>
                        <strong>{cred.website}</strong> ({cred.username})
                      </CredentialItem>
                    ))}
                  </DuplicateGroup>
                ))}
              </div>
            </IssueSection>
          )}

          {/* All Strong - Success Message */}
          {auditReport.weak_passwords.length === 0 &&
            auditReport.breached_passwords.length === 0 &&
            auditReport.duplicate_passwords.length === 0 &&
            auditReport.summary.total > 0 && (
              <SuccessMessage style={{ marginTop: '2rem', textAlign: 'center' }}>
                🎉 Excellent! All your credentials are secure. Keep it up!
              </SuccessMessage>
            )}

          {auditReport.summary.total === 0 && (
            <EmptyState>
              <p>No credentials to audit yet. Add some credentials first!</p>
            </EmptyState>
          )}

          <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #e0e0e0' }}>
            <Button onClick={handleRunAudit} style={{ marginRight: '1rem' }}>
              🔄 Run Audit Again
            </Button>
          </div>
        </>
      )}
    </AuditContainer>
  );
}

export default SecurityAudit;
