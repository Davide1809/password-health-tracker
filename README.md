# Password Health Tracker

## Project Overview
Password Health Tracker is a web application designed to help users monitor and improve password security. The MVP focuses on user account management and password strength checking, providing real-time feedback and AI-assisted suggestions.

## Features

### MVP (Sprint 1)
- User Account Management
  - Signup / Login
- Password Strength Checker
  - Real-time feedback on password security

### Future Features (Sprint 2+)
- Password History Tracking
- Password Reset
- AI Suggestions for stronger passwords
- Security Insights

## Technology Stack
- Frontend: React.js
- Backend: Python / Flask
- Database: MongoDB
- AI Integration: GitHub Copilot, ChatGPT
- Deployment: Docker, Google Cloud Platform (Cloud Run)
- CI/CD: GitHub Actions

## User Management - Signup Feature

**User Story:** As a new user, I want to create an account so that I can access the application.

**Feature Status:** MVP Completed

### Functionality
- New users can register with email and password
- Email format validation (frontend + backend)
- Password security requirements:
  - At least 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one symbol
- Confirmation message on successful registration
- Redirect to dashboard after signup
- Error messages for invalid inputs or already registered emails

### AI Tools Used
- **GitHub Copilot**: Assisted in React components (`Signup.jsx`) and helper functions (`validators.js`)
- **ChatGPT**: Helped design backend API, validation logic, and suggested security best practices

### Setup Instructions for Signup Feature
1. **Backend Setup (Flask + MongoDB)**

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py

# ✔ Story 2: Login Feature

**User Story:**  
_As a returning user, I want to log in so that I can access my personal dashboard._

**Status:** Completed ✅

---

## Functionality
- Users log in with their registered email and password  
- Password verification uses secure hashing (`check_password_hash`)  
- Flask-Login creates a session (`login_user()`)  
- Redirects user to dashboard after successful login  
- Invalid login attempts return a **generic error**  
- Protected API endpoints require authentication using `@login_required`

---

## Backend Implementation Details (Flask + MongoDB)

### 🔐 Login Route
**POST `/api/login`**  
- Validates email and password  
- Fetches user from MongoDB  
- Verifies hashed password  
- Creates authenticated user session  
- Returns JSON response  

### 🔐 Session Management
Using **Flask-Login**:
- `login_user()` — logs user in  
- `current_user` — access logged-in user  
- `logout_user()` — logs user out  
- `@login_required` — restricts protected routes  

### 🛡 Security Enhancements
- Cookies enabled with:
  ```python
  CORS(app, supports_credentials=True)

No plaintext passwords (only hashed)
	•	Generic login error prevents attacker email enumeration
	•	Session cookies managed securely by Flask

⸻

Frontend Implementation Details (React)

🔑 Login.jsx
	•	Collects email & password
	•	Sends POST request including credentials:
fetch("http://127.0.0.1:5001/api/login", {
  method: "POST",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password }),
});

	Shows success or error messages
	•	Redirects to /dashboard on success

⸻

Testing Summary
	•	✔ Valid login → success + redirect
	•	✔ Wrong password → error
	•	✔ Wrong email → same generic error
	•	✔ Attempt to access /dashboard without login → blocked
	•	✔ Refresh after login → session persists

⸻

AI Tools Used

GitHub Copilot
	•	Assisted React form logic
	•	Helped auto-generate JSX input handling

ChatGPT
	•	Designed backend login flow
	•	Implemented session-based authentication
	•	Helped debug CORS credential issues
	•	Ensured best practices for password security

⸻

How to Run the Login Feature (Backend)
cd backend
source .venv/bin/activate
python app.py

How to Run the Frontend (React)
cd frontend
npm install
npm start

# Story 3 – Password Strength Analyzer

**Description:** 
Implement a password strength analyzer component that allows users to input a password and receive a strength evaluation. This ensures users can create strong and secure passwords.

**Status:** Completed

Components Added/Modified:
	•	PasswordAnalyzer.jsx – Component to input and analyze password strength.
	•	passwordStrength.js – Utility functions to calculate password strength.
	•	App.js – Added route /analyze to render the PasswordAnalyzer component.
	•	App.test.js – Updated tests to verify correct rendering of routes including the password analyzer.

Acceptance Criteria:
	1.	Users can navigate to /analyze.
	2.	Users can input a password and click “Analyze.”
	3.	Password strength is evaluated and displayed (Weak / Medium / Strong).
	4.	Component renders correctly without breaking other routes.
	5.	All unit and integration tests pass.

Testing:
	•	Used React Testing Library to ensure routing and component rendering works.
	•	Verified password strength logic with passwordStrength.test.js.
	•	All tests are passing as of this commit.