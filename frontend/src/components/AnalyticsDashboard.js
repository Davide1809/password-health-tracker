import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { getApiBase } from '../config';

const DashboardContainer = styled.div`
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

const ChartContainer = styled.div`
  margin-bottom: 2rem;

  h3 {
    color: #333;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }
`;

const BarChart = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 6px;
  min-height: 250px;
`;

const Bar = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;

  .bar-column {
    width: 100%;
    background: ${props => props.color};
    border-radius: 4px 4px 0 0;
    transition: all 0.3s ease;
    cursor: pointer;

    &:hover {
      opacity: 0.8;
      transform: translateY(-5px);
    }
  }

  .bar-label {
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.5rem;
    text-align: center;
    font-weight: 500;
  }

  .bar-value {
    font-weight: 600;
    color: #333;
    margin-top: 0.25rem;
  }
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: linear-gradient(135deg, ${props => props.gradient} 0%, ${props => props.gradient2} 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;

  h4 {
    margin: 0;
    font-size: 0.9rem;
    opacity: 0.9;
    font-weight: 600;
  }

  .value {
    font-size: 2rem;
    font-weight: bold;
    margin: 0.5rem 0 0 0;
  }

  .subtitle {
    font-size: 0.8rem;
    opacity: 0.85;
    margin-top: 0.5rem;
  }
`;

const PieChart = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 6px;

  svg {
    width: 200px;
    height: 200px;
  }
`;

const Legend = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;

  .color-box {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    background: ${props => props.color};
  }

  .label {
    color: #333;
    font-weight: 500;
  }

  .value {
    color: #666;
    margin-left: auto;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem 1rem;
  color: #999;

  p {
    font-size: 1rem;
    margin: 0;
  }
`;

const LoadingMessage = styled.div`
  text-align: center;
  padding: 2rem;
  color: #666;
`;

function AnalyticsDashboard() {
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchCredentials();
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
      setCredentials(response.data.credentials || []);
    } catch (error) {
      console.error('Failed to fetch credentials:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (password.length >= 16) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;

    if (strength <= 1) return 'Weak';
    if (strength <= 2) return 'Weak';
    if (strength <= 3) return 'Fair';
    if (strength <= 4) return 'Strong';
    return 'Very Strong';
  };

  // Calculate analytics data
  const getAnalyticsData = () => {
    if (credentials.length === 0) {
      return null;
    }

    const strengthCounts = {
      'Weak': 0,
      'Fair': 0,
      'Strong': 0,
      'Very Strong': 0
    };

    const breachedCount = credentials.filter(c => c.breach_status === true).length;
    const safeCount = credentials.length - breachedCount;

    credentials.forEach(cred => {
      const strength = calculatePasswordStrength(cred.password);
      strengthCounts[strength]++;
    });

    const avgPasswordLength = Math.round(
      credentials.reduce((sum, cred) => sum + (cred.password ? cred.password.length : 0), 0) /
      credentials.length
    );

    return {
      strengthCounts,
      breachedCount,
      safeCount,
      avgPasswordLength,
      totalCredentials: credentials.length
    };
  };

  const analyticsData = getAnalyticsData();

  if (loading) {
    return (
      <DashboardContainer>
        <Title>📊 Analytics Dashboard</Title>
        <LoadingMessage>Loading analytics...</LoadingMessage>
      </DashboardContainer>
    );
  }

  if (!analyticsData) {
    return (
      <DashboardContainer>
        <Title>📊 Analytics Dashboard</Title>
        <EmptyState>
          <p>No credentials saved yet. Add some credentials to see analytics!</p>
        </EmptyState>
      </DashboardContainer>
    );
  }

  const maxCount = Math.max(
    ...Object.values(analyticsData.strengthCounts),
    analyticsData.breachedCount,
    analyticsData.safeCount
  );

  const strengthColors = {
    'Weak': '#f44336',
    'Fair': '#ff9800',
    'Strong': '#8bc34a',
    'Very Strong': '#4caf50'
  };

  const breachColors = {
    'Breached': '#f44336',
    'Safe': '#4caf50'
  };

  return (
    <DashboardContainer>
      <Title>📊 Analytics Dashboard</Title>

      {/* Key Statistics */}
      <StatGrid>
        <StatCard gradient="#667eea" gradient2="#8bc34a">
          <h4>Total Credentials</h4>
          <div className="value">{analyticsData.totalCredentials}</div>
        </StatCard>

        <StatCard gradient="#4caf50" gradient2="#81c784">
          <h4>Safe Passwords</h4>
          <div className="value">{analyticsData.safeCount}</div>
          <div className="subtitle">
            {Math.round((analyticsData.safeCount / analyticsData.totalCredentials) * 100)}% of total
          </div>
        </StatCard>

        <StatCard gradient="#f44336" gradient2="#ef5350">
          <h4>Breached Passwords</h4>
          <div className="value">{analyticsData.breachedCount}</div>
          <div className="subtitle">
            {Math.round((analyticsData.breachedCount / analyticsData.totalCredentials) * 100)}% of total
          </div>
        </StatCard>

        <StatCard gradient="#2196f3" gradient2="#64b5f6">
          <h4>Average Length</h4>
          <div className="value">{analyticsData.avgPasswordLength}</div>
          <div className="subtitle">characters</div>
        </StatCard>
      </StatGrid>

      {/* Password Strength Distribution */}
      <ChartContainer>
        <h3>🔐 Password Strength Distribution</h3>
        <BarChart>
          {Object.entries(analyticsData.strengthCounts).map(([strength, count]) => (
            <Bar key={strength} color={strengthColors[strength]}>
              <div
                className="bar-column"
                style={{
                  height: maxCount > 0 ? `${(count / maxCount) * 150}px` : '10px'
                }}
              />
              <div className="bar-label">{strength}</div>
              <div className="bar-value">{count}</div>
            </Bar>
          ))}
        </BarChart>
      </ChartContainer>

      {/* Breach Status Distribution */}
      <ChartContainer>
        <h3>🛡️ Breach Status Overview</h3>
        <BarChart>
          {[
            { label: 'Safe', count: analyticsData.safeCount, color: breachColors['Safe'] },
            { label: 'Breached', count: analyticsData.breachedCount, color: breachColors['Breached'] }
          ].map(({ label, count, color }) => (
            <Bar key={label} color={color}>
              <div
                className="bar-column"
                style={{
                  height: maxCount > 0 ? `${(count / maxCount) * 150}px` : '10px'
                }}
              />
              <div className="bar-label">{label}</div>
              <div className="bar-value">{count}</div>
            </Bar>
          ))}
        </BarChart>
      </ChartContainer>

      {/* Strength Breakdown */}
      <ChartContainer>
        <h3>📈 Detailed Breakdown</h3>
        <Legend>
          {Object.entries(analyticsData.strengthCounts).map(([strength, count]) => (
            <LegendItem key={strength}>
              <div className="color-box" style={{ background: strengthColors[strength] }} />
              <div className="label">{strength} Passwords</div>
              <div className="value">
                {count} ({Math.round((count / analyticsData.totalCredentials) * 100)}%)
              </div>
            </LegendItem>
          ))}
          <LegendItem style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e0e0e0' }}>
            <div className="color-box" style={{ background: '#4caf50' }} />
            <div className="label">Breach Safe</div>
            <div className="value">
              {analyticsData.safeCount} ({Math.round((analyticsData.safeCount / analyticsData.totalCredentials) * 100)}%)
            </div>
          </LegendItem>
          <LegendItem>
            <div className="color-box" style={{ background: '#f44336' }} />
            <div className="label">Breach Found</div>
            <div className="value">
              {analyticsData.breachedCount} ({Math.round((analyticsData.breachedCount / analyticsData.totalCredentials) * 100)}%)
            </div>
          </LegendItem>
        </Legend>
      </ChartContainer>

      {/* Insights */}
      <ChartContainer style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #e0e0e0' }}>
        <h3>💡 Insights & Recommendations</h3>
        <div style={{ background: '#f0f4ff', padding: '1rem', borderRadius: '6px', lineHeight: '1.6', color: '#333' }}>
          {analyticsData.strengthCounts['Weak'] + analyticsData.strengthCounts['Fair'] > 0 && (
            <p>
              ⚠️ You have <strong>{analyticsData.strengthCounts['Weak'] + analyticsData.strengthCounts['Fair']} weak or fair strength passwords</strong>. 
              Consider upgrading these to stronger passwords with at least 12 characters including uppercase, lowercase, numbers, and special characters.
            </p>
          )}

          {analyticsData.breachedCount > 0 && (
            <p>
              🚨 <strong>{analyticsData.breachedCount} of your passwords have been found in data breaches</strong>. 
              Change these passwords immediately to protect your accounts.
            </p>
          )}

          {analyticsData.avgPasswordLength < 12 && (
            <p>
              📏 Your average password length is {analyticsData.avgPasswordLength} characters. 
              Aim for at least 12-16 characters for better security.
            </p>
          )}

          {analyticsData.strengthCounts['Weak'] + analyticsData.strengthCounts['Fair'] === 0 &&
            analyticsData.breachedCount === 0 && (
              <p>
                🎉 <strong>Great job!</strong> All your passwords are strong and safe. Keep maintaining this security level by regularly updating weak passwords and monitoring for breaches.
              </p>
            )}
        </div>
      </ChartContainer>
    </DashboardContainer>
  );
}

export default AnalyticsDashboard;
