"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
import re
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
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
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
        user = User(email=email, password_hash=User.hash_password(password))
        result = mongo.db.users.insert_one(user.to_dict())
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(result.inserted_id),
            'email': email
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
                'email': user_data['email']
            },
            'expires_in': 86400  # 24 hours in seconds
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logged out successfully'}), 200


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
