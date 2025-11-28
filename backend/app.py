import os
import secrets
import json
import re
import base64
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 


# --- Helper Functions for Encryption ---

def get_fernet_key(secret_key):
    """
    Generates a URL-safe Base64 encoded Fernet key from the Flask SECRET_KEY.
    Ensures the key is 32 bytes long for Fernet's requirement.
    """
    # Pad or truncate the secret key to 32 bytes and base64url encode it
    key_bytes = secret_key.encode('utf-8')
    padded_key = key_bytes.ljust(32)[:32]
    return base64.urlsafe_b64encode(padded_key)

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
    # We rely on the browser's session for cookie expiration or explicit logout.
)

# Allow CORS only from the frontend URL, and allow credentials (cookies)
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

# --- Encryption Setup ---
# The Fernet key MUST be derived from the application's SECRET_KEY
if app.config.get('SECRET_KEY'):
    try:
        ENCRYPTION_KEY = get_fernet_key(app.config['SECRET_KEY'])
        fernet = Fernet(ENCRYPTION_KEY)
    except Exception as e:
        print(f"Error initializing Fernet: {e}. Check SECRET_KEY length/format.")
        fernet = None
else:
    print("WARNING: SECRET_KEY not set. Encryption will fail.")
    fernet = None

def encrypt_data(data):
    """Encrypts a string using Fernet."""
    if not fernet:
        raise RuntimeError("Encryption failed: Fernet not initialized.")
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """Decrypts a base64-encoded encrypted string using Fernet."""
    if not fernet:
        raise RuntimeError("Decryption failed: Fernet not initialized.")
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption Error: {e}")
        return "[Decryption Failed]" # Return a safe placeholder on error

# --- Database Setup (MongoDB) ---
try:
    client = MongoClient(MONGO_URI)
    db = client.password_health_tracker
    users_collection = db.users
    passwords_collection = db.passwords 
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    client = None
    db = None
    users_collection = None
    passwords_collection = None


# --- Authentication Decorator ---
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Check for user existence
        user = users_collection.find_one({'_id': user_id})
        if not user:
            # User ID in session but user not in DB (stale session)
            session.clear()
            return jsonify({'message': 'Unauthorized or session expired'}), 401

        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/api/user_info', methods=['GET'])
@require_auth
def user_info():
    user_id = session.get('user_id')
    user = users_collection.find_one({'_id': user_id})
    if user:
        # Generate a display name from email (e.g., "john.doe" from "john.doe@example.com")
        display_name = user['email'].split('@')[0].replace('.', ' ').title()
        return jsonify({
            'email': user['email'],
            'userName': display_name
        }), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    
    # Store the user's primary credentials
    user_id = secrets.token_urlsafe(16)
    users_collection.insert_one({
        '_id': user_id,
        'email': email,
        'password_hash': hashed_password,
        'created_at': datetime.utcnow()
    })
    
    # CRITICAL: Log user in immediately upon successful signup
    session['user_id'] = user_id
    
    response = make_response(jsonify({'message': 'User created and logged in.'}), 201)
    return response

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['_id']
        response = make_response(jsonify({'message': 'Login successful'}), 200)
        return response
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    # This also handles the browser closing (window.onunload)
    session.clear()
    response = make_response(jsonify({'message': 'Logged out successfully'}), 200)
    # Explicitly clear the session cookie
    response.set_cookie(app.config['SESSION_COOKIE_NAME'], '', expires=0, secure=True, httponly=True, samesite='None')
    return response

# --- Password Health Routes ---

@app.route('/api/analyze', methods=['POST'])
def analyze_password():
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'message': 'Missing password'}), 400

    # zxcvbn returns score from 0 (terrible) to 4 (excellent)
    results = zxcvbn(password)
    
    return jsonify({
        'score': results['score'],
        'feedback': results['feedback']
    }), 200

@app.route('/api/passwords', methods=['POST'])
@require_auth
def add_password():
    user_id = session.get('user_id')
    data = request.get_json()
    site_name = data.get('site_name')
    username = data.get('username')
    password = data.get('password')

    if not all([site_name, username, password]):
        return jsonify({'message': 'Missing data fields'}), 400

    try:
        encrypted_password = encrypt_data(password)
    except RuntimeError as e:
        return jsonify({'message': str(e)}), 500

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
        try:
            decrypted_password = decrypt_data(doc['encrypted_password'])
        except Exception:
            decrypted_password = "[Decryption Failed]"

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

# --- Startup for Local Testing ---
if __name__ == '__main__':
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        app.config['SECRET_KEY'] = 'default_secret_key_for_local_dev_123456789012'
        MONGO_URI = 'mongodb://localhost:27017' # Default MongoDB connection for local testing
        FRONTEND_URL = 'http://localhost:3000'
        
        # Re-initialize encryption and DB connections if running locally
        ENCRYPTION_KEY = get_fernet_key(app.config['SECRET_KEY'])
        fernet = Fernet(ENCRYPTION_KEY)
        try:
            client = MongoClient(MONGO_URI)
            db = client.password_health_tracker
            users_collection = db.users
            passwords_collection = db.passwords
        except Exception as e:
            print(f"Error connecting to local MongoDB: {e}")

    app.run(debug=True, port=8080)