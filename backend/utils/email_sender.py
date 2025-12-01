"""
Email sending utilities for password reset and notifications
"""
import os
import logging
from flask_mail import Mail, Message

logger = logging.getLogger(__name__)

# Global mail instance
mail = None


def init_mail(app):
    """
    Initialize Flask-Mail with application config
    
    Args:
        app: Flask application instance
    """
    global mail
    
    # Configure mail settings from environment variables
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@passwordhealthtracker.com')
    
    mail = Mail(app)
    logger.info('✉️ Flask-Mail initialized')
    
    return mail


def send_password_reset_email(recipient_email, reset_token):
    """
    Send password reset email to user
    
    Args:
        recipient_email (str): Email address to send reset link to
        reset_token (str): JWT reset token
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if not mail:
            logger.error('✉️ Mail not initialized')
            return False
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/forgot-password?token={reset_token}"
        
        subject = "Password Reset Request - Password Health Tracker"
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                    .button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; font-size: 0.9rem; color: #666; }}
                    .warning {{ background: #fff3cd; color: #856404; padding: 10px; border-radius: 4px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>We received a request to reset your password for your Password Health Tracker account. If you didn't make this request, you can ignore this email.</p>
                        
                        <p><strong>To reset your password, click the button below:</strong></p>
                        
                        <center>
                            <a href="{reset_link}" class="button">Reset Password</a>
                        </center>
                        
                        <p>Or copy and paste this link in your browser:</p>
                        <p><small>{reset_link}</small></p>
                        
                        <div class="warning">
                            <strong>⚠️ Security Notice:</strong> This link will expire in 1 hour for your security.
                        </div>
                        
                        <p>If you have any questions, feel free to contact our support team.</p>
                        
                        <p>Best regards,<br><strong>Password Health Tracker Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                        <p>&copy; 2024 Password Health Tracker. All rights reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hello,
        
        We received a request to reset your password. If you didn't make this request, please ignore this email.
        
        To reset your password, visit this link:
        {reset_link}
        
        This link will expire in 1 hour for your security.
        
        Best regards,
        Password Health Tracker Team
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=html_body,
            body=text_body
        )
        
        mail.send(msg)
        logger.info(f'✉️ Password reset email sent to {recipient_email}')
        return True
        
    except Exception as e:
        logger.error(f'✉️ Failed to send password reset email to {recipient_email}: {str(e)}')
        return False


def send_notification_email(recipient_email, subject, message_body):
    """
    Send generic notification email
    
    Args:
        recipient_email (str): Email address to send notification to
        subject (str): Email subject
        message_body (str): Email body (plain text or HTML)
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if not mail:
            logger.error('✉️ Mail not initialized')
            return False
        
        msg = Message(
            subject=subject,
            recipients=[recipient_email],
            html=message_body
        )
        
        mail.send(msg)
        logger.info(f'✉️ Notification email sent to {recipient_email}')
        return True
        
    except Exception as e:
        logger.error(f'✉️ Failed to send notification email to {recipient_email}: {str(e)}')
        return False
