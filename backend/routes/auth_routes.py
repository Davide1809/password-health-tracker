"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
import re
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from models.user import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Get MongoDB instance (will be injected from app)
mongo = None

def set_mongo(mongo_instance):
    """Set the MongoDB instance for routes"""
    global mongo
    mongo = mongo_instance


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> tuple:
    """
    Validate password meets security requirements
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*...)")
    
    if errors:
        return False, " ".join(errors)
    
    return True, None


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Check if user already exists
        if mongo.db.users.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(email=email, password_hash=User.hash_password(password), name=name)
        result = mongo.db.users.insert_one(user.to_dict())
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(result.inserted_id),
            'email': email,
            'name': name
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Find user by email
        user_data = mongo.db.users.find_one({'email': email})
        
        if not user_data or not User.verify_password(password, user_data['password_hash']):
            # Don't reveal which field is incorrect
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        jwt_secret = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
        token = jwt.encode(
            {
                'user_id': str(user_data['_id']),
                'email': user_data['email'],
                'name': user_data.get('name', 'User'),
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            jwt_secret,
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user_data['_id']),
                'email': user_data['email'],
                'name': user_data.get('name', 'User')
            },
            'expires_in': 86400  # 24 hours in seconds
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logged out successfully'}), 200


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset - sends reset link to email"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email or not validate_email(email):
            return jsonify({'error': 'Valid email is required'}), 400
        
        # Find user
        user_data = mongo.db.users.find_one({'email': email})
        
        if not user_data:
            # Don't reveal if email exists (security best practice)
            return jsonify({
                'message': 'If email exists in system, password reset link will be sent'
            }), 200
        
        # Generate reset token (valid for 1 hour)
        reset_token = jwt.encode(
            {
                'user_id': str(user_data['_id']),
                'email': email,
                'type': 'password_reset',
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            os.environ.get('JWT_SECRET_KEY', 'dev-secret-key'),
            algorithm='HS256'
        )
        
        # Store reset token in database (optional for validation)
        mongo.db.password_resets.insert_one({
            'email': email,
            'token': reset_token,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=1)
        })
        
        # TODO: Send email with reset link
        # For now, return token (in production, send via email)
        reset_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        return jsonify({
            'message': 'Password reset link sent to email',
            'reset_link': reset_link  # TODO: Remove in production, only send via email
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Password reset request failed: {str(e)}'}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using valid reset token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        reset_token = data.get('token', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not reset_token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        # Validate password strength
        is_valid, error_message = validate_password_strength(new_password)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Verify reset token
        try:
            jwt_secret = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
            payload = jwt.decode(reset_token, jwt_secret, algorithms=['HS256'])
            
            if payload.get('type') != 'password_reset':
                return jsonify({'error': 'Invalid reset token'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Reset token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid reset token'}), 401
        
        # Update password
        user_id = payload.get('user_id')
        email = payload.get('email')
        
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id), 'email': email},
            {
                '$set': {
                    'password_hash': User.hash_password(new_password),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'User not found'}), 404
        
        # Remove used reset token
        mongo.db.password_resets.delete_one({'token': reset_token})
        
        return jsonify({
            'message': 'Password reset successful',
            'email': email
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500


@bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token validity"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'valid': False, 'error': 'Missing token'}), 401
        
        jwt_secret = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        
        return jsonify({
            'valid': True,
            'user_id': payload.get('user_id'),
            'email': payload.get('email')
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 500
