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
    # REMOVED: PERMANENT_SESSION_LIFETIME=timedelta(hours=24) 
    # By removing this, the session cookie becomes a browser-session cookie,
    # meaning it expires when the browser is closed.
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
    # Derive a 32-byte key from the secret key for Fernet
    key_bytes = secret_key.encode('utf-8')
    key_base64 = base64.urlsafe_b64encode(key_bytes.ljust(32)[:32])
    return key_base64

try:
    ENCRYPTION_KEY = get_fernet_key(app.config['SECRET_KEY'])
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing Fernet encryption: {e}")
    fernet = None

# --- Utility Functions ---

def hash_password(password):
    """Hashes the password using Werkzeug's secure method."""
    return generate_password_hash(password)

def check_password(raw_password, hashed_password):
    """Checks a raw password against a hashed one."""
    return check_password_hash(hashed_password, raw_password)

def check_email_format(email):
    """Simple email format validation."""
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$'
    return re.match(email_regex, email) is not None

def check_password_strength(password):
    """
    Checks password strength using traditional complexity rules AND zxcvbn score.
    Returns True if score >= 3 AND all complexity rules are met, False otherwise.
    Complexity Rules: Min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 symbol.
    """
    MIN_LENGTH = 8
    if len(password) < MIN_LENGTH:
        return False
        
    has_uppercase = any(c.isupper() for c in password)
    has_lowercase = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    
    complexity_met = has_uppercase and has_lowercase and has_digit and has_symbol
    
    if not complexity_met:
        return False

    zxcvbn_score = zxcvbn(password)['score']
    
    return zxcvbn_score >= 3


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

    if not check_password_strength(password): 
        analysis = zxcvbn(password)
        
        feedback_messages = [analysis['feedback']['warning'] or "Password is not strong enough."]
        
        if len(password) < 8:
             feedback_messages.append("Must be at least 8 characters long.")
        if not any(c.isupper() for c in password):
            feedback_messages.append("Must include at least one uppercase letter.")
        if not any(c.islower() for c in password):
            feedback_messages.append("Must include at least one lowercase letter.")
        if not any(c.isdigit() for c in password):
            feedback_messages.append("Must include at least one number.")
        if not any(not c.isalnum() for c in password):
            feedback_messages.append("Must include at least one symbol/special character.")
            
        detailed_feedback = ". ".join(sorted(list(set(feedback_messages))))
        
        return jsonify({'message': f'Password failed strength check. {detailed_feedback}'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already in use'}), 409

    hashed_password = hash_password(password)

    user_info = users_collection.insert_one({
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow()
    })

    # Ensure session is non-permanent (will rely on the browser session)
    session.permanent = False 
    session['user_id'] = str(user_info.inserted_id)
    session['email'] = email
    
    return jsonify({'message': 'User created and logged in successfully', 'email': email}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})

    if user and check_password(password, user['password']): 
        # Set session to non-permanent
        session.permanent = False 
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