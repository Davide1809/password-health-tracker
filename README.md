# Password Health Tracker

A web-based application designed to help users evaluate the strength and safety of their passwords through real-time strength assessments, breach detection, and AI-powered recommendations.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

- **Password Strength Scoring** - Real-time analysis using advanced algorithms (zxcvbn)
- **Breach Detection** - Check passwords against the "Have I Been Pwned" database
- **AI Recommendations** - AI-powered suggestions using OpenAI's ChatGPT
- **User Dashboard** - Track password analysis history and trends
- **Privacy-First Design** - Passwords are never stored or transmitted insecurely
- **User Authentication** - Secure JWT-based authentication
- **Responsive UI** - Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

### Technology Stack

- **Backend**: Python with Flask
- **Frontend**: React 18 with styled-components
- **Database**: MongoDB
- **Containerization**: Docker & Docker Compose
- **Deployment**: Google Cloud Platform (Cloud Run, Kubernetes)
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: Terraform
- **APIs**: 
  - Have I Been Pwned (Breach Detection)
  - OpenAI (AI Recommendations)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (Browser)                         │
│                      React Frontend                          │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────┴──────────────────────────────────┐
│                     API Gateway / Nginx                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────┐    ┌────────▼──────┐   ┌──────▼─────┐
│  Flask     │    │   MongoDB     │   │  External  │
│  Backend   │    │   Database    │   │   APIs     │
│  (REST)    │    │               │   │ (HIBP,OAI) │
└────────────┘    └───────────────┘   └────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- MongoDB (or MongoDB Atlas)
- OpenAI API Key (for AI recommendations)
- Have I Been Pwned API Key (optional, for premium features)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/password-health-tracker.git
   cd password-health-tracker
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - MongoDB: localhost:27017

### Local Development

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_ENV=development
python app.py
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### Password Analysis Endpoints

#### Analyze Password
```http
POST /api/passwords/analyze
Content-Type: application/json

{
  "password": "MyPassword123!@#"
}

Response:
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

#### Check Breach Status
```http
POST /api/breaches/check
Content-Type: application/json

{
  "password": "MyPassword123!@#"
}

Response:
{
  "breached": false,
  "breach_count": 0,
  "message": "Password not found in breaches"
}
```

#### Get AI Recommendations
```http
POST /api/ai/recommendations
Content-Type: application/json
Authorization: Bearer <token>

{
  "password": "weakpassword"
}

Response:
{
  "original_password": "***",
  "recommendations": [
    "Increase password length to 16+ characters",
    "Add more special characters for complexity",
    "Avoid common words or dictionary terms",
    "Use a mix of uppercase and lowercase letters",
    "Include numbers throughout the password"
  ]
}
```

### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📦 Project Structure

```
password-health-tracker/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   ├── routes/               # API route blueprints
│   │   ├── auth_routes.py
│   │   ├── password_routes.py
│   │   ├── breach_routes.py
│   │   └── ai_routes.py
│   ├── utils/                # Utility modules
│   │   ├── password_analyzer.py
│   │   ├── breach_checker.py
│   │   └── ai_recommender.py
│   ├── models/               # Database models
│   └── tests/                # Unit tests
├── frontend/
│   ├── package.json          # Node dependencies
│   ├── public/               # Static files
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── index.js
│       ├── index.css
│       ├── components/       # React components
│       │   └── Navigation.js
│       └── pages/            # Page components
│           ├── Dashboard.js
│           ├── PasswordChecker.js
│           ├── Results.js
│           └── About.js
├── deployment/               # Deployment configurations
│   ├── k8s-deployment.yaml   # Kubernetes manifests
│   ├── terraform.tf          # Terraform configuration
│   └── terraform.tfvars.example
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # GitHub Actions CI/CD
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile.backend        # Backend container image
├── Dockerfile.frontend       # Frontend container image
├── nginx.conf               # Nginx configuration
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# MongoDB
MONGO_URI=mongodb://admin:password@localhost:27017/password_health?authSource=admin

# Security
JWT_SECRET_KEY=your-secret-key-change-in-production

# External APIs
OPENAI_API_KEY=your-openai-api-key
HIBP_API_KEY=your-hibp-api-key
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install pytest pytest-cov
pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Monitoring & Logging

### Backend Logging
Logs are output to console and can be configured in `app.py`:
```python
logging.basicConfig(level=logging.INFO)
```

### Application Metrics
- Health check endpoint: `GET /api/health`
- Version endpoint: `GET /api/version`

## 🚢 Deployment

### Docker Compose (Development)
```bash
docker-compose up --build
```

### Kubernetes (Production)
```bash
kubectl apply -f deployment/k8s-deployment.yaml
```

### Google Cloud Run (via GitHub Actions)
Push to `main` branch to trigger automatic deployment:
1. Backend deploys to: `https://password-tracker-backend-[ID].run.app`
2. Frontend deploys to: `https://password-tracker-frontend-[ID].run.app`

### Terraform (Infrastructure as Code)
```bash
cd deployment
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## 🔐 Security Considerations

1. **Password Handling**
   - Passwords are never stored in logs
   - Only hashed for HIBP API checks
   - Never transmitted in plain text

2. **API Security**
   - JWT token-based authentication
   - CORS properly configured
   - Input validation on all endpoints
   - Rate limiting recommended

3. **Data Protection**
   - HTTPS/TLS in production
   - Database encryption at rest
   - Sensitive data in environment variables
   - Regular security audits recommended

4. **Best Practices**
   - Keep dependencies updated
   - Use secrets management (Google Secret Manager, AWS Secrets Manager)
   - Enable audit logging
   - Implement rate limiting
   - Monitor for suspicious activity

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Have I Been Pwned** - For providing the breach database API
- **OpenAI** - For ChatGPT API integration
- **Zxcvbn** - For password strength estimation algorithm
- **Flask** - Backend framework
- **React** - Frontend framework
- **MongoDB** - Database

## 📞 Contact & Support

- **Email**: support@passwordhealthtracker.com
- **GitHub Issues**: [Report an issue](https://github.com/yourusername/password-health-tracker/issues)
- **Documentation**: [Full documentation](https://docs.passwordhealthtracker.com)

## 🗺️ Roadmap

- [ ] Two-factor authentication (2FA)
- [ ] Password manager integration
- [ ] Browser extensions (Chrome, Firefox, Safari)
- [ ] Mobile applications (iOS, Android)
- [ ] Advanced analytics dashboard
- [ ] Dark mode UI
- [ ] Multi-language support
- [ ] Offline password checking capability
- [ ] Machine learning for anomaly detection
- [ ] Integration with identity theft monitoring services

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Status**: Active Development
