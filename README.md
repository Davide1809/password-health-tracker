# Password Health Tracker

## Project Overview
Password Health Tracker is a web application designed to help users monitor and improve the strength of their passwords. It evaluates password security, tracks password history, and provides AI-powered suggestions to create stronger credentials. The application aims to enhance online security awareness and promote best practices for managing passwords.

---

## Features

### MVP (Sprint 1)
- **User Account Management**
  - Sign up / Log in
- **Password Strength Checker**
  - Real-time feedback on password security

### Future Features (Sprint 2)
- **Password History Tracking**
  - View previously used passwords
- **Password Reset**
  - Recover access if the user forgets their password
- **AI Suggestions**
  - Receive AI-generated recommendations for stronger passwords
- **Security Insights**
  - AI-powered analysis of password health trends

---

## Technology Stack
- **Frontend:** React.js  
- **Backend:** Node.js / Express  
- **Database:** MongoDB  
- **AI Integration:** GitHub Copilot, ChatGPT  
- **Deployment:** Docker, Google Cloud Platform (Cloud Run)  
- **CI/CD:** GitHub Actions

---

## Getting Started

### Clone the repository
```bash
git clone https://github.com/Davide1809/Password-Health-Tracker.git
cd Password-Health-Tracker

## User Management - Signup Feature

**User Story:** As a new user, I want to create an account so that I can access the application.

**Feature Status:** MVP Completed

### Functionality
- New users can register by providing an email and password.
- Email format is validated on the frontend and backend.
- Passwords must meet security requirements: 
  - At least 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one symbol
- Users receive a confirmation message upon successful registration.
- Users are redirected to the dashboard after signup.
- Error messages are displayed for invalid emails, weak passwords, or if the email is already registered.

### AI Tools Used
- **GitHub Copilot:** Assisted in writing React components (`Signup.jsx`) and validators (`validators.js`).
- **ChatGPT:** Helped design API logic, email/password validation, and suggested best practices for password security.

### Setup Instructions for Signup Feature
1. **Backend Setup (Flask + MongoDB)**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python app.py