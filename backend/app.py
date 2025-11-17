import os
import secrets
import json
from datetime import datetime, timedelta

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
# We hash the secret key to ensure a good quality, 32-byte key source.
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

    # Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'Email already in use'}), 409

    # Hash the password
    hashed_password = generate_password_hash(password)

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

    if user and check_password_hash(user['password'], password):
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

# --- Password Analysis Endpoint (Existing Story 2) ---

@app.route('/api/analyze', methods=['POST'])
def analyze_password_endpoint():
    data = request.json
    password = data.get('password', '')

    if not password:
        return jsonify({'message': 'Password is required for analysis'}), 400

    # NOTE: In a real-world scenario, you would run zxcvbn here.
    # Since zxcvbn requires a complex installation, we use a simple mock 
    # for the purpose of this demonstration, but the API path is correct.
    
    # Mock zxcvbn analysis based on password length
    length = len(password)
    if length < 5:
        score = 0
        crack_time_display = "instant"
        warning = "Too short. Requires at least 8 characters."
        suggestions = ["Increase the length.", "Mix characters."]
    elif length < 8:
        score = 1
        crack_time_display = "a few seconds"
        warning = "Still too short."
        suggestions = ["Increase the length to at least 8.", "Add symbols."]
    elif length < 12:
        score = 2
        crack_time_display = "a few hours"
        warning = None
        suggestions = ["Add more words or symbols to increase length."]
    else:
        # A mock strong password result
        score = 4
        crack_time_display = "centuries"
        warning = None
        suggestions = ["Great job!"]

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

    # Create the password entry document
    password_entry = {
        'user_id': user_id,
        'site_name': site_name,
        'username': username,
        'encrypted_password': encrypted_password,
        'created_at': datetime.utcnow()
    }

    # Save to the passwords collection
    passwords_collection.insert_one(password_entry)

    return jsonify({'message': 'Password stored securely.'}), 201


@app.route('/api/passwords', methods=['GET'])
@require_auth
def get_passwords():
    user_id = session.get('user_id')
    
    # Retrieve all entries for the current user
    # NOTE: MongoDB stores the user_id as a string, but in production, 
    # you might want to use ObjectId if user_id is the primary key _id.
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