# Password Health Tracker - Setup Guide

## Initial Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/password-health-tracker.git
cd password-health-tracker

# Configure backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 3. Development Setup

#### Option A: Using Docker Compose (Recommended)
```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
# MongoDB: localhost:27017
```

#### Option B: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
npm start
```

### 4. API Keys Required

1. **OpenAI API Key** (for AI recommendations)
   - Get from: https://platform.openai.com/api-keys
   - Add to `backend/.env`: `OPENAI_API_KEY=your-key`

2. **Have I Been Pwned API Key** (optional)
   - Get from: https://haveibeenpwned.com/API/v3
   - Add to `backend/.env`: `HIBP_API_KEY=your-key`

### 5. Testing the Application

#### Health Check
```bash
curl http://localhost:5000/api/health
```

#### Test Password Analysis
```bash
curl -X POST http://localhost:5000/api/passwords/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "TestPassword123!"}'
```

### 6. Next Steps

- Review API documentation in README.md
- Set up CI/CD in GitHub Actions
- Configure GCP credentials for cloud deployment
- Deploy to production environment

## Troubleshooting

### MongoDB Connection Issues
```bash
# Verify MongoDB is running
docker ps | grep mongodb

# Check logs
docker logs password_tracker_mongodb
```

### Backend Import Errors
```bash
# Reinstall dependencies
pip install -r backend/requirements.txt

# Verify Python path
export PYTHONPATH=$PYTHONPATH:.
```

### Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Environment Configuration

See `backend/.env.example` for all available environment variables.
