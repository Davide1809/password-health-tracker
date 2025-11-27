import os
import secrets
import json
import re
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 
import base64

# --- Configuration and Initialization ---
app = Flask(__name__)

# Load environment variables (set during gcloud deploy)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
MONGO_URI = os.environ.get('MONGO_URI')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

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
    passwords_collection = db.passwords 
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# --- Encryption Setup ---
def get_fernet_key(secret_key):
    key_bytes = secret_key.encode('utf-8')
    key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
    return key_base64

try:
    ENCRYPTION_KEY = get_fernet_key(app.config['SECRET_KEY'])
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing Fernet encryption: {e}")
    fernet = None

# --- Utility Functions (Fixed for Test Compatibility) ---

def hash_password(password):
    """Hashes the password using Werkzeug's secure method."""
    return generate_password_hash(password)

# FIX 1: Defined signature to match test call (raw_password, hashed_password)
def check_password(raw_password, hashed_password):
    """Checks a raw password against a hashed one.
       Uses (raw, hashed) signature to match unit tests.
       Internal call uses Werkzeug's required (hashed, raw) order."""
    return check_password_hash(hashed_password, raw_password)

def check_email_format(email):
    """Simple email format validation."""
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$'
    return re.match(email_regex, email) is not None

# FIX 2: Returns boolean (True if strong enough, False otherwise) to satisfy unit test assertions
def check_password_strength(password):
    """Checks password strength using zxcvbn. Returns True if score >= 3, False otherwise."""
    return zxcvbn(password)['score'] >= 3

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
    decorated.__name__ = f.__name__ 
    return decorated

# --- User Authentication Endpoints ---

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400
        
    if not check_email_format(email):
        return jsonify({'message': 'Invalid email format'}), 400

    # Using the fixed boolean check_password_strength
    if not check_password_strength(password): 
        # Re-run zxcvbn just to get the detailed feedback for the user
        analysis = zxcvbn(password)
        warning = analysis['feedback']['warning'] or "Password is not strong enough."
        return jsonify({'message': warning + " Please use a stronger password (Score 3 or higher is required)."}), 400

    # Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already in use'}), 409

    # Hash the password
    hashed_password = hash_password(password)

    # Insert new user into MongoDB
    users_collection.insert_one({
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow()
    })

    # Auto-login after signup
    session['user_id'] = str(users_collection.find_one({'email': email})['_id'])
    session['email'] = email
    return jsonify({'message': 'User created and logged in successfully', 'email': email}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})

    # Call check_password with the new (raw_password, hashed_password) order
    if user and check_password(password, user['password']): 
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

# --- Password Analysis Endpoint (Uses real zxcvbn) ---

@app.route('/api/analyze', methods=['POST'])
def analyze_password_endpoint():
    data = request.json
    password = data.get('password', '')

    if not password:
        return jsonify({'message': 'Password is required for analysis'}), 400

    analysis = zxcvbn(password)
    
    return jsonify({
        'score': analysis['score'],
        'crack_time_display': analysis['crack_time_display'],
        'feedback': analysis['feedback']
    }), 200


# --- Password Management Endpoints ---

@app.route('/api/passwords', methods=['POST'])
@require_auth
def save_password():
    data = request.json
    user_id = session.get('user_id')
    
    if not all(key in data for key in ['site_name', 'username', 'password']):
        return jsonify({'message': 'Missing fields: site_name, username, and password are required.'}), 400

    site_name = data['site_name']
    username = data['username']
    raw_password = data['password']

    encrypted_password = encrypt_data(raw_password)
    if encrypted_password is None:
        return jsonify({'message': 'Encryption failed. Check server setup.'}), 500

    password_entry = {
        'user_id': user_id,
        'site_name': site_name,
        'username': username,
        'encrypted_password': encrypted_password,
        'created_at': datetime.utcnow()
    }

    passwords_collection.insert_one(password_entry)

    return jsonify({'message': 'Password stored securely.'}), 201


@app.route('/api/passwords', methods=['GET'])
@require_auth
def get_passwords():
    user_id = session.get('user_id')
    
    cursor = passwords_collection.find({'user_id': user_id}).sort('created_at', -1)
    
    passwords_list = []
    for doc in cursor:
        decrypted_password = decrypt_data(doc['encrypted_password'])
        
        passwords_list.append({
            'id': str(doc['_id']),
            'site_name': doc['site_name'],
            'username': doc['username'],
            'password': decrypted_password, 
            'created_at': doc['created_at'].isoformat()
        })
        
    return jsonify(passwords_list), 200

# --- Error Handling ---

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'message': 'Resource not found'}), 404


if __name__ == '__main__':
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        app.config['SECRET_KEY'] = 'default_secret_key_for_local_dev_123456789012345678901234'
        os.environ['MONGO_URI'] = 'mongodb://localhost:27017/'
        
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))