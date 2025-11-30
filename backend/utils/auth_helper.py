"""
Authentication helper functions and decorators
"""
import jwt
import os
from functools import wraps
from flask import request, jsonify
from datetime import datetime

JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')


def get_token_from_request(request_obj):
    """
    Extract JWT token from request headers
    
    Args:
        request_obj: Flask request object
        
    Returns:
        str or None: JWT token if present
    """
    auth_header = request_obj.headers.get('Authorization', '')
    
    if not auth_header:
        return None
    
    parts = auth_header.split()
    
    if len(parts) != 2:
        return None
    
    if parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def verify_jwt_token(token):
    """
    Verify JWT token and extract payload
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        dict or None: Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


def token_required(f):
    """
    Decorator to protect routes that require authentication
    
    Usage:
        @app.route('/api/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': 'Protected data', 'user': current_user})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request(request)
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Pass current user info to the route
        return f(*args, current_user=payload, **kwargs)
    
    return decorated
