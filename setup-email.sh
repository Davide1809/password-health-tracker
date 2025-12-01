#!/bin/bash

# Email Configuration Setup Script
# This script helps you configure email sending for the Password Health Tracker

echo "🔐 Password Health Tracker - Email Configuration Setup"
echo "======================================================"
echo ""

# Check if .env file exists
if [ -f "backend/.env" ]; then
    echo "✅ Found existing backend/.env file"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing .env file"
        exit 0
    fi
fi

echo ""
echo "Choose your email provider:"
echo "1) Gmail (recommended)"
echo "2) SendGrid"
echo "3) Office 365"
echo "4) AWS SES"
echo "5) Custom SMTP"
echo ""
read -p "Enter your choice (1-5): " -r

case $REPLY in
    1)
        echo ""
        echo "📧 Gmail Setup Instructions:"
        echo "1. Go to myaccount.google.com → Security"
        echo "2. Enable 2-Step Verification (if not already)"
        echo "3. Go to Security → App passwords"
        echo "4. Select Mail and Windows Computer, get your 16-char password"
        echo ""
        
        read -p "Enter your Gmail address: " -r MAIL_USERNAME
        read -p "Enter your 16-character app password (without spaces): " -r MAIL_PASSWORD
        
        MAIL_SERVER="smtp.gmail.com"
        MAIL_PORT="587"
        MAIL_USE_TLS="True"
        ;;
    2)
        echo ""
        echo "📧 SendGrid Setup Instructions:"
        echo "1. Get your API key from SendGrid dashboard"
        echo ""
        
        read -p "Enter your SendGrid API key: " -r MAIL_PASSWORD
        MAIL_USERNAME="apikey"
        MAIL_SERVER="smtp.sendgrid.net"
        MAIL_PORT="587"
        MAIL_USE_TLS="True"
        ;;
    3)
        echo ""
        echo "📧 Office 365 Setup Instructions:"
        echo ""
        
        read -p "Enter your Office 365 email: " -r MAIL_USERNAME
        read -p "Enter your Office 365 password: " -r MAIL_PASSWORD
        MAIL_SERVER="smtp.office365.com"
        MAIL_PORT="587"
        MAIL_USE_TLS="True"
        ;;
    4)
        echo ""
        echo "📧 AWS SES Setup Instructions:"
        echo "1. Get your SMTP credentials from AWS SES console"
        echo ""
        
        read -p "Enter your AWS region (e.g., us-east-1): " -r AWS_REGION
        read -p "Enter your SMTP username: " -r MAIL_USERNAME
        read -p "Enter your SMTP password: " -r MAIL_PASSWORD
        MAIL_SERVER="email-smtp.${AWS_REGION}.amazonaws.com"
        MAIL_PORT="587"
        MAIL_USE_TLS="True"
        ;;
    5)
        echo ""
        read -p "Enter SMTP server: " -r MAIL_SERVER
        read -p "Enter SMTP port: " -r MAIL_PORT
        read -p "Enter username: " -r MAIL_USERNAME
        read -p "Enter password: " -r MAIL_PASSWORD
        read -p "Use TLS? (true/false): " -r MAIL_USE_TLS
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
read -p "Enter default sender email (e.g., noreply@passwordhealthtracker.com): " -r MAIL_DEFAULT_SENDER
read -p "Enter frontend URL (e.g., http://localhost:3000): " -r FRONTEND_URL

# Create .env file
echo "Creating backend/.env file..."
cat > "backend/.env" << EOF
# Email Configuration
MAIL_SERVER=${MAIL_SERVER}
MAIL_PORT=${MAIL_PORT}
MAIL_USE_TLS=${MAIL_USE_TLS}
MAIL_USERNAME=${MAIL_USERNAME}
MAIL_PASSWORD=${MAIL_PASSWORD}
MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER}
FRONTEND_URL=${FRONTEND_URL}

# Other environment variables (add as needed)
# JWT_SECRET_KEY=your-secret-key
# OPENAI_API_KEY=your-api-key
# MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/database
# CREDENTIAL_ENCRYPTION_KEY=your-encryption-key
EOF

echo ""
echo "✅ Email configuration saved to backend/.env"
echo ""
echo "Next steps:"
echo "1. Update any other environment variables in backend/.env as needed"
echo "2. Never commit .env file to git (already in .gitignore)"
echo "3. Test email setup by running the backend:"
echo "   cd backend && python app.py"
echo "4. Then request a password reset to test"
echo ""
echo "📚 For more details, see EMAIL_SETUP.md"
