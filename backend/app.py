import os
import secrets
import json
from datetime import datetime, timedelta
import re # Added for email format validation
from zxcvbn import zxcvbn # Added for password strength checking

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import base64

# --- Configuration and Initialization ---
app = Flask(__name__)

# Load environment variables (set during gcloud deploy)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
MONGO_URI = os.environ.get('MONGO_URI')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# CI/CD Test Comment: 2025-11-27

# Configure session cookies for secure cross-site interaction
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24) # Session lasts 24 hours
)

# Allow CORS only from the frontend URL, and allow credentials (cookies)
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

# --- Database Setup (MongoDB) ---
try:
    client = MongoClient(MONGO_URI)
    db = client.password_health_tracker
    users_collection = db.users
    passwords_collection = db.passwords # New collection for stored passwords
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    # In a real app, you might crash here or implement better retry logic

# --- Encryption Setup ---
# Derive a Fernet key from the SECRET_KEY for AES-256 encryption.
# Fernet keys must be 32 URL-safe base64-encoded bytes.
def get_fernet_key(secret_key):
    # Use the first 32 bytes of the secret key hash and base64 encode it
    key_bytes = secret_key.encode('utf-8')
    key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
    return key_base64

try:
    ENCRYPTION_KEY = get_fernet_key(app.config['SECRET_KEY'])
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing Fernet encryption: {e}")
    fernet = None

# --- UTILITY FUNCTIONS (Added to fix ImportError in tests) ---

def hash_password(password):
    """Hashes a password using werkzeug.security."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Checks a password against a hash using werkzeug.security."""
    return check_password_hash(hashed_password, password)

def check_email_format(email):
    """Checks if the email format is valid using regex."""
    return re.match(r'[^@]+@[^@]+\.[^@]+', email) is not None

def check_password_strength(password):
    """Uses zxcvbn to check password strength and returns a score (0-4)."""
    # zxcvbn returns score from 0 (terrible) to 4 (strong)
    results = zxcvbn(password)
    return results['score']

# --- Helpers for Encryption/Decryption ---
def encrypt_data(data):
    """Encrypts a string using Fernet."""
    if not fernet:
        return None
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """Decrypts a Fernet-encrypted string."""
    if not fernet:
        return "Encryption Error"
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption failed: {e}")
        return "Decryption Error"

# --- Authentication Helpers ---
def require_auth(f):
    """Decorator to ensure user is authenticated."""
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__ # Needed for Flask routing
    return decorated

# --- User Authentication Endpoints (Existing) ---

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    # Validate email format
    if not check_email_format(email):
        return jsonify({'message': 'Invalid email format'}), 400

    # Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already in use'}), 409

    # Check password strength (Enforce minimum score of 3 for signup)
    if check_password_strength(password) < 3:
        return jsonify({'message': 'Password is too weak. Score must be 3 or higher.'}), 400

    # Hash the password
    hashed_password = hash_password(password)

    # Insert new user into MongoDB
    users_collection.insert_one({
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow()
    })

    # Auto-login after signup
    user = users_collection.find_one({'email': email})
    session['user_id'] = str(user['_id'])
    session['email'] = user['email']
    return jsonify({'message': 'User created and logged in successfully', 'email': email}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})

    if user and check_password(user['password'], password):
        # Set session variable on successful login
        session['user_id'] = str(user['_id'])
        session['email'] = user['email']
        return jsonify({'message': 'Logged in successfully', 'email': user['email']}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/dashboard', methods=['GET'])
@require_auth
def dashboard():
    email = session.get('email')
    return jsonify({'message': f'Welcome back, {email}!'}), 200

# --- Password Analysis Endpoint (Now uses real zxcvbn) ---

@app.route('/api/analyze', methods=['POST'])
def analyze_password_endpoint():
    data = request.json
    password = data.get('password', '')

    if not password:
        return jsonify({'message': 'Password is required for analysis'}), 400
    
    # Use actual zxcvbn analysis
    results = zxcvbn(password)
    score = results['score']
    
    # Format crack time from seconds to a human-readable string
    crack_time_s = results['crack_times_seconds']['offline_fast_hashing_1e10_per_second']
    
    if crack_time_s < 1:
        crack_time_display = "instantly"
    elif crack_time_s < 60:
        crack_time_display = f"in about {int(crack_time_s)} seconds"
    elif crack_time_s < 3600:
        crack_time_display = f"in about {int(crack_time_s / 60)} minutes"
    elif crack_time_s < 86400:
        crack_time_display = f"in about {int(crack_time_s / 3600)} hours"
    elif crack_time_s < 31536000:
        crack_time_display = f"in about {int(crack_time_s / 86400)} days"
    else:
        crack_time_display = f"in about {int(crack_time_s / 31536000)} years"

    # Extract feedback
    warning = results['feedback']['warning']
    suggestions = results['feedback']['suggestions']

    return jsonify({
        'score': score,
        'crack_time_display': crack_time_display,
        'feedback': {
            'warning': warning,
            'suggestions': suggestions
        }
    }), 200


# --- NEW: Password Management Endpoints (Story 3) ---

@app.route('/api/passwords', methods=['POST'])
@require_auth
def save_password():
    data = request.json
    user_id = session.get('user_id')
    
    # Validate required fields
    if not all(key in data for key in ['site_name', 'username', 'password']):
        return jsonify({'message': 'Missing fields: site_name, username, and password are required.'}), 400

    site_name = data['site_name']
    username = data['username']
    raw_password = data['password']

    # CRITICAL STEP: Encrypt the sensitive password before storing
    encrypted_password = encrypt_data(raw_password)
    if encrypted_password is None:
        return jsonify({'message': 'Encryption failed. Check server setup.'}), 500
        
    # Get strength score for health check dashboard
    strength_score = check_password_strength(raw_password)

    # Create the password entry document
    password_entry = {
        'user_id': user_id,
        'site_name': site_name,
        'username': username,
        'encrypted_password': encrypted_password,
        'strength_score': strength_score, # Store strength score
        'created_at': datetime.utcnow()
    }

    # Save to the passwords collection
    passwords_collection.insert_one(password_entry)

    return jsonify({'message': 'Password stored securely.', 'strength_score': strength_score}), 201


@app.route('/api/passwords', methods=['GET'])
@require_auth
def get_passwords():
    user_id = session.get('user_id')
    
    # Retrieve all entries for the current user, sorting by newest first
    cursor = passwords_collection.find({'user_id': user_id}).sort('created_at', -1)
    
    passwords_list = []
    for doc in cursor:
        # CRITICAL STEP: Decrypt the password for display
        decrypted_password = decrypt_data(doc['encrypted_password'])
        
        passwords_list.append({
            'id': str(doc['_id']),
            'site_name': doc['site_name'],
            'username': doc['username'],
            'password': decrypted_password, # The decrypted, raw password
            'strength_score': doc.get('strength_score', 0), # Include strength score
            'created_at': doc['created_at'].isoformat()
        })
        
    return jsonify(passwords_list), 200

# --- Error Handling ---

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'message': 'Resource not found'}), 404


if __name__ == '__main__':
    # When running locally, set environment variables explicitly
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        # Provide sensible defaults for local testing if necessary
        app.config['SECRET_KEY'] = 'default_secret_key_for_local_dev'
        os.environ['MONGO_URI'] = 'mongodb://localhost:27017/'
        
    # Remove the host/port settings for Cloud Run deployment
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))