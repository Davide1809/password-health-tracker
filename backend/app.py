import os
import secrets
import json
import re
from datetime import datetime, timedelta
from functools import wraps
from bson.objectid import ObjectId

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 
import base64

# --- Configuration and Initialization ---\napp = Flask(__name__)\n\n# Load environment variables (set during gcloud deploy)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
MONGO_URI = os.environ.get('MONGO_URI')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Configure session cookies for secure cross-site interaction
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
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
    print(f"Error connecting to MongoDB: {e}")
    # In a real environment, you might want to exit or use a fallback
    client = None
    db = None
    users_collection = None
    passwords_collection = None

# --- Encryption Setup ---
# Derive encryption key from SECRET_KEY for Fernet. 
# It must be 32 URL-safe base64-encoded bytes.
# We'll use a SHA256 hash of the SECRET_KEY, then base64 encode it.
def get_fernet_key(secret_key):
    import hashlib
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_hash[:32])

# Initialize Fernet instance
if app.config['SECRET_KEY']:
    FERNET_KEY = get_fernet_key(app.config['SECRET_KEY'])
    fernet = Fernet(FERNET_KEY)
else:
    # Use a dummy key if running without a real secret key
    fernet = Fernet(b'default_fernets_key_for_testing_00') 

def encrypt_data(data):
    """Encrypts a string using Fernet."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data):
    """Decrypts a Fernet token string."""
    try:
        return fernet.decrypt(data.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return "[Decryption Error]"

# --- Authentication Decorator ---

def require_auth(f):
    """Decorator to ensure the user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Utility Functions ---

def is_strong_password(password):
    """
    Checks password strength using zxcvbn.
    A score of 3 or higher is considered strong.
    """
    # Score 0=very weak, 1=weak, 2=okay, 3=good, 4=strong
    result = zxcvbn(password)
    # Also enforce minimum length for basic checks before zxcvbn
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if result['score'] < 3:
        return False, result['feedback']['warning'] or "Password is too weak."
    return True, "Password is strong."

# --- Routes ---

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_name = data.get('user_name')

    if not all([email, password, user_name]):
        return jsonify({'message': 'Missing required fields.'}), 400
    
    # 1. Check password strength
    is_strong, feedback = is_strong_password(password)
    if not is_strong:
        return jsonify({'message': feedback}), 400

    # 2. Check if user already exists
    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists.'}), 409

    # 3. Hash password and store user
    hashed_password = generate_password_hash(password)
    user_entry = {
        'email': email,
        'user_name': user_name,
        'password_hash': hashed_password,
        'created_at': datetime.utcnow()
    }
    result = users_collection.insert_one(user_entry)
    user_id = str(result.inserted_id)

    # 4. Create session
    session['user_id'] = user_id
    session['user_name'] = user_name
    
    return jsonify({'message': 'User registered and logged in successfully.', 'user_name': user_name}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'Missing required fields.'}), 400

    # 1. Find user
    user = users_collection.find_one({'email': email})

    # 2. Verify password
    if user and check_password_hash(user['password_hash'], password):
        # 3. Create session
        user_id = str(user['_id'])
        user_name = user.get('user_name', 'User')

        session['user_id'] = user_id
        session['user_name'] = user_name

        return jsonify({'message': 'Login successful.', 'user_name': user_name}), 200
    else:
        return jsonify({'message': 'Invalid credentials.'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """
    Clears the session on the backend. This is essential for security.
    Flask's session.clear() deletes the data, but the browser still holds the cookie.
    We need to return a response that tells the browser to destroy the session cookie.
    """
    if 'user_id' in session:
        session.clear()
        
    # Create a response object
    response = make_response(jsonify({'message': 'Logout successful. Session cleared.'}), 200)
    
    # Instruct the browser to clear the session cookie by setting it to expire immediately.
    # We must use the same settings (Secure, SameSite) as when it was created.
    # Flask session cookies are named 'session' by default.
    # Note: Flask's session.clear() generally handles cookie deletion on the response, 
    # but explicitly creating the response ensures we can be certain.
    
    # Since we rely on the default Flask session cookie mechanism:
    # 1. session.clear() removes the session data from the server-side store (if any).
    # 2. Flask marks the session cookie for deletion in the response header.
    # We just ensure the response is correctly returned.
    
    return response

@app.route('/api/passwords', methods=['POST'])
@require_auth
def add_password():
    data = request.get_json()
    site_name = data.get('site_name')
    username = data.get('username')
    password = data.get('password')

    if not all([site_name, username, password]):
        return jsonify({'message': 'Missing required password fields.'}), 400

    user_id = session.get('user_id')
    
    # Encrypt the sensitive password data before storing
    encrypted_password = encrypt_data(password)

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
    
    # Retrieve passwords for the current user, sorted by creation date (newest first)
    cursor = passwords_collection.find({'user_id': user_id}).sort('created_at', -1)
    
    passwords_list = []
    for doc in cursor:
        decrypted_password = decrypt_data(doc['encrypted_password'])
        
        passwords_list.append({
            'id': str(doc['_id']),
            'site_name': doc['site_name'],
            'username': doc['username'],
            'password': decrypted_password, # Decrypt before sending to the frontend
            'created_at': doc['created_at'].isoformat()
        })
        
    return jsonify(passwords_list), 200

@app.route('/api/passwords/<password_id>', methods=['DELETE'])
@require_auth
def delete_password(password_id):
    user_id = session.get('user_id')

    # Validate if the ID is a valid MongoDB ObjectId format
    if not ObjectId.is_valid(password_id):
        return jsonify({'message': 'Invalid password ID format.'}), 400

    # Convert string ID to ObjectId
    obj_id = ObjectId(password_id)

    # Delete the document, ensuring it belongs to the current user
    result = passwords_collection.delete_one({
        '_id': obj_id, 
        'user_id': user_id
    })

    if result.deleted_count == 1:
        return jsonify({'message': 'Password deleted successfully.'}), 200
    else:
        return jsonify({'message': 'Password not found or unauthorized.'}), 404


# --- Error Handling ---

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'message': 'Resource not found'}), 404


if __name__ == '__main__':
    # Default values for local testing only
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        app.config['SECRET_KEY'] = 'default_secret_key_for_local_dev_12345678'
        if 'FERNET_KEY' not in globals():
             FERNET_KEY = get_fernet_key(app.config['SECRET_KEY'])
             fernet = Fernet(FERNET_KEY)
    
    # For local development with a local MongoDB instance
    if not os.environ.get('MONGO_URI'):
        MONGO_URI = 'mongodb://localhost:27017/'
        try:
             client = MongoClient(MONGO_URI)
             db = client.password_health_tracker
             users_collection = db.users
             passwords_collection = db.passwords
             print("Connected to local MongoDB.")
        except Exception as e:
             print(f"Error connecting to local MongoDB: {e}")
             
    # Running the Flask app
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))