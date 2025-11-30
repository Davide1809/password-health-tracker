# Password Health Tracker - Development Instructions

This file provides workspace-specific custom instructions for GitHub Copilot.

## Project Overview

**Name:** Password Health Tracker  
**Type:** Full-stack web application  
**Status:** Active Development  
**Last Updated:** January 2024

## Tech Stack

- **Backend:** Python (Flask) on port 5000
- **Frontend:** React 18 on port 3000
- **Database:** MongoDB
- **Containerization:** Docker & Docker Compose
- **Deployment:** Google Cloud Platform
- **CI/CD:** GitHub Actions
- **APIs:** Have I Been Pwned, OpenAI

## Project Structure

```
password-health-tracker/
├── backend/              # Flask REST API
├── frontend/             # React SPA
├── deployment/           # K8s, Terraform configs
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml    # Local development
```

## Key Features to Implement

1. **Password Strength Analysis** - Real-time scoring using zxcvbn
2. **Breach Detection** - Integration with Have I Been Pwned
3. **AI Recommendations** - OpenAI ChatGPT integration
4. **User Dashboard** - History and analytics
5. **Authentication** - JWT-based auth

## Development Guidelines

### Backend (Python/Flask)

- Use Blueprint pattern for route organization
- Add input validation on all endpoints
- Include proper error handling
- Use environment variables for configuration
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Use type hints for function parameters

### Frontend (React)

- Use functional components with hooks
- Implement styled-components for styling
- Follow component-based architecture
- Use React Router for navigation
- Handle loading and error states
- Implement proper error boundaries

### Common Tasks

**Run Docker Compose:**
```bash
docker-compose up --build
```

**Install Backend Dependencies:**
```bash
cd backend && pip install -r requirements.txt
```

**Install Frontend Dependencies:**
```bash
cd frontend && npm install
```

**Run Backend:**
```bash
cd backend && python app.py
```

**Run Frontend:**
```bash
cd frontend && npm start
```

## API Guidelines

- All endpoints return JSON
- Use proper HTTP status codes
- Implement consistent error responses
- Document all endpoints in API_DOCUMENTATION.md
- Use authentication headers: `Authorization: Bearer <token>`

## Important Files

- `README.md` - Project overview and setup
- `API_DOCUMENTATION.md` - Complete API reference
- `SETUP.md` - Quick start guide
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Node dependencies
- `docker-compose.yml` - Local environment config

## Security Practices

- Never log or store passwords
- Use HTTPS in production
- Validate all user inputs
- Implement rate limiting
- Use environment variables for secrets
- Hash passwords with bcrypt
- Implement CORS properly

## Testing Requirements

- Unit tests for critical functions
- Integration tests for API endpoints
- At least 80% code coverage
- Test error handling scenarios

## Deployment Checklist

- [ ] Set environment variables
- [ ] Update API documentation
- [ ] Run all tests
- [ ] Build Docker images
- [ ] Update CHANGELOG.md
- [ ] Tag release in git
- [ ] Deploy via GitHub Actions

## Common Patterns

### Creating a New API Endpoint

1. Create route in `backend/routes/new_routes.py`
2. Import and register blueprint in `app.py`
3. Add utility functions in `backend/utils/`
4. Document in `API_DOCUMENTATION.md`
5. Add tests in `backend/tests/`

### Adding Frontend Component

1. Create component in `frontend/src/components/`
2. Add styling with styled-components
3. Import in parent component or page
4. Update navigation if needed
5. Test responsiveness

## Debugging Tips

- Backend logs: `docker logs password_tracker_backend`
- Frontend logs: Browser console (F12)
- Database: `docker logs password_tracker_mongodb`
- API testing: Use curl or Postman

## Git Workflow

- Branch naming: `feature/description` or `fix/description`
- Commit format: `type(scope): description`
- Always pull before pushing
- Create PR for review

## Resources

- API Docs: `API_DOCUMENTATION.md`
- Setup Guide: `SETUP.md`
- Contributing: `CONTRIBUTING.md`
- Main README: `README.md`

## Next Priority Tasks

1. Complete backend route implementations
2. Add comprehensive error handling
3. Implement user authentication
4. Add unit tests
5. Deploy to development environment
6. Create admin dashboard
7. Add analytics features

---

**Last Updated:** January 2024  
**Maintained by:** Password Health Tracker Team
