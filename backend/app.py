import os
import secrets
import json
import re
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS # Keep this import
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 
import base64

# --- Configuration and Initialization ---\n
app = Flask(__name__)

# Load environment variables (set during gcloud deploy)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
MONGO_URI = os.environ.get('MONGO_URI')
# FRONTEND_URL is no longer used for CORS, but kept for context if needed elsewhere.
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Configure session cookies for secure cross-site interaction
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
)

# --- CRITICAL CORS FIX ---
# To support dynamic frontend URLs (like the Canvas preview) while allowing cookies (credentials),
# we must use resources='/*' and allow all origins in the dictionary.
CORS(
    app, 
    resources={r"/*": {"origins": "*"}}, # Allow all origins for all routes
    supports_credentials=True, # MUST be True to allow session cookies
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS", "DELETE"] # Ensure all necessary methods are allowed
)
# --- END CRITICAL CORS FIX ---


# --- Database Setup (MongoDB) ---
try:
    client = MongoClient(MONGO_URI)
    db = client.password_health_tracker
    users_collection = db.users
    passwords_collection = db.passwords 
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # In a real app, you might crash here if the database is essential

# --- Encryption/Decryption Setup (Fernet) ---\n# The ENCRYPTION_KEY must be a URL-safe base64-encoded 32-byte key.
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', secrets.token_urlsafe(32))
# Fernet expects the key to be 32 base64-urlsafe bytes
try:
    if len(ENCRYPTION_KEY) != 43 or not all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in ENCRYPTION_KEY):
         # If the environment variable isn't set properly, use a dummy key for local testing.
        print("WARNING: ENCRYPTION_KEY not properly configured. Using default/dummy key.")
        ENCRYPTION_KEY = base64.urlsafe_b64encode(b'a' * 32).decode() 
    
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing Fernet: {e}")
    fernet = None # Handle case where key is invalid


def encrypt_data(data):
    if fernet:
        return fernet.encrypt(data.encode()).decode()
    return data # Fallback if Fernet failed to initialize

def decrypt_data(token):
    if fernet:
        try:
            return fernet.decrypt(token.encode()).decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return token
    return token


# --- Authentication Decorator ---\n
def require_auth(f):
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required. Please log in.'}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__ # Required for Flask to recognize the route function name
    return decorated


# --- Routes ---\n
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
    user_id = users_collection.insert_one({
        'email': email,
        'password_hash': hashed_password,
        'created_at': datetime.utcnow()
    }).inserted_id

    # Log in the user immediately after signup
    session['user_id'] = str(user_id)
    session['email'] = email

    return jsonify({'message': 'User created and logged in', 'email': email}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password_hash'], password):
        # Set session cookie
        session['user_id'] = str(user['_id'])
        session['email'] = email
        return jsonify({'message': 'Login successful', 'email': email}), 200
    
    return jsonify({'message': 'Invalid email or password'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/api/analyze', methods=['POST'])
@require_auth
def analyze_password_route():
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({'message': 'Missing password parameter'}), 400
    
    # Use zxcvbn to analyze password strength
    # Note: zxcvbn is a blocking operation, but generally fast for short strings.
    analysis_result = zxcvbn(password)
    
    # Structure the relevant results for the frontend
    result = {
        'password': password,
        'score': analysis_result['score'], # 0 (worst) to 4 (best)
        'crack_time_display': analysis_result['crack_times_display']['online_throttling_100_per_hour'],
        'feedback': analysis_result['feedback']
    }
    
    # Return the analysis result
    return jsonify(result), 200


@app.route('/api/passwords', methods=['POST'])
@require_auth
def add_password():
    data = request.get_json()
    site_name = data.get('site_name')
    username = data.get('username')
    password = data.get('password')

    if not site_name or not username or not password:
        return jsonify({'message': 'Missing data fields'}), 400
    
    encrypted_password = encrypt_data(password)
    user_id = session.get('user_id')

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
    
    # Fetch all passwords for the user, sorted by creation date (newest first)
    cursor = passwords_collection.find({'user_id': user_id}).sort('created_at', -1)
    
    passwords_list = []
    for doc in cursor:
        # Decrypt the password before sending it to the client
        decrypted_password = decrypt_data(doc['encrypted_password'])
        
        passwords_list.append({
            'id': str(doc['_id']),
            'site_name': doc['site_name'],
            'username': doc['username'],
            'password': decrypted_password, 
            'created_at': doc['created_at'].isoformat()
        })
        
    return jsonify(passwords_list), 200

# --- Error Handling ---\n
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'message': 'Resource not found'}), 404


if __name__ == '__main__':
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        app.config['SECRET_KEY'] = 'default_secret_key_for_local_dev'
        os.environ['MONGO_URI'] = 'mongodb://localhost:27017/test' 
        # Note: Local MongoDB connection requires a local instance running
        
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))