import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
`;

const Card = styled.div`
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
`;

function Results() {
  return (
    <Container>
      <Card>
        <h2>Your Analysis Results</h2>
        <p>Results from your password analysis will appear here.</p>
      </Card>
    </Container>
  );
}

export default Results;
