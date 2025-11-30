# API Documentation

## Base URL
```
Development: http://localhost:5000/api
Production: https://api.passwordhealthtracker.com
```

## Authentication
All endpoints requiring authentication use JWT tokens in the Authorization header:
```
Authorization: Bearer <token>
```

## Response Format
All responses are JSON with the following structure:
```json
{
  "data": {},
  "error": null,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Endpoints

### Auth Endpoints

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!@#"
}
```

**Response (201):**
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "message": "User registered successfully"
}
```

#### POST /auth/login
Login and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123!@#"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com"
  }
}
```

### Password Endpoints

#### POST /passwords/analyze
Analyze password strength (No authentication required).

**Request:**
```json
{
  "password": "MyPassword123!@#"
}
```

**Response (200):**
```json
{
  "strength": {
    "score": 4,
    "strength": "Very Strong",
    "crack_time": "centuries",
    "feedback": "Password is strong",
    "suggestions": [],
    "entropy": 72.5,
    "characteristics": {
      "length": 15,
      "has_lowercase": true,
      "has_uppercase": true,
      "has_digits": true,
      "has_special": true,
      "common_patterns": []
    }
  },
  "breached": false,
  "breach_count": 0,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /passwords/history
Get password analysis history (Requires authentication).

**Response (200):**
```json
{
  "history": [
    {
      "id": "507f1f77bcf86cd799439011",
      "analyzed_at": "2024-01-01T12:00:00Z",
      "strength_score": 4,
      "breached": false
    }
  ]
}
```

### Breach Endpoints

#### POST /breaches/check
Check if password has been breached (No authentication required).

**Request:**
```json
{
  "password": "MyPassword123!@#"
}
```

**Response (200):**
```json
{
  "breached": false,
  "breach_count": 0,
  "message": "Password not found in breaches"
}
```

#### POST /breaches/search
Search breaches by email (Requires authentication).

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "email": "user@example.com",
  "breaches": [
    {
      "name": "LinkedIn",
      "title": "LinkedIn",
      "domain": "linkedin.com",
      "breach_date": "2021-06-22",
      "added_date": "2021-06-22",
      "modified_date": "2021-06-22",
      "data_classes": ["Email addresses", "Passwords"]
    }
  ],
  "breach_count": 1
}
```

### AI Endpoints

#### POST /ai/recommendations
Get AI-powered password recommendations (Requires authentication).

**Request:**
```json
{
  "password": "weakpassword"
}
```

**Response (200):**
```json
{
  "original_password": "***",
  "recommendations": [
    "Increase password length to 16+ characters",
    "Add more special characters for complexity",
    "Avoid common words or dictionary terms",
    "Use a mix of uppercase and lowercase letters"
  ]
}
```

#### POST /ai/generate
Generate a strong password (Requires authentication).

**Request:**
```json
{
  "requirements": {
    "length": 16,
    "use_special": true,
    "use_numbers": true
  }
}
```

**Response (200):**
```json
{
  "generated_password": "K9x@2mP!5qL8vN",
  "strength_score": 95
}
```

### Health Endpoints

#### GET /health
Check API health status.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /version
Get API version.

**Response (200):**
```json
{
  "version": "1.0.0",
  "name": "Password Health Tracker API"
}
```

## Error Responses

### 400 - Bad Request
```json
{
  "error": "Missing email or password"
}
```

### 401 - Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 404 - Not Found
```json
{
  "error": "Endpoint not found"
}
```

### 500 - Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

- Public endpoints: 100 requests per minute
- Authenticated endpoints: 500 requests per minute
- Breach check: 10 requests per minute

## CORS Configuration

Allowed origins in production:
- https://passwordhealthtracker.com
- https://www.passwordhealthtracker.com

## WebSocket Support (Future)

Real-time password strength feedback will be available via WebSocket at:
```
ws://localhost:5000/ws/password-check
```
