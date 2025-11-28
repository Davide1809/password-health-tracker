import os
import secrets
import json
import re
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 
import base64

# New imports for database operations
from bson.objectid import ObjectId
from bson.errors import InvalidId

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
    # We rely on the browser's session cookie behavior (expires on close)
)

# Allow CORS only from the frontend URL, and allow credentials (cookies)
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

# --- Database Setup (MongoDB) ---
# Initialize collections as None to allow for mocking in tests
client = None
db = None
users_collection = None
passwords_collection = None
is_db_connected = False

try:
    # Attempt to connect to the real MongoDB instance
    client = MongoClient(MONGO_URI)
    db = client.password_health_tracker
    users_collection = db.users
    passwords_collection = db.passwords 
    # Check connection by running a simple command
    client.admin.command('ping')
    is_db_connected = True
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"FATAL: Failed to connect to MongoDB: {e}")
    # In a real environment, you might stop the app. For testing, we allow it to proceed
    # so the mocked client can be used later.

# --- Security and Helpers ---

# Encryption key derived from SECRET_KEY
FERNET_KEY = base64.urlsafe_b64encode(app.config['SECRET_KEY'][:32].encode().ljust(32, b'\x00'))
cipher_suite = Fernet(FERNET_KEY)

def encrypt_data(data):
    """Encrypts a plaintext string."""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(token):
    """Decrypts an encrypted token."""
    try:
        return cipher_suite.decrypt(token.encode()).decode()
    except Exception as e:
        print(f"Decryption failed: {e}")
        return "Decryption Error" # Return a placeholder on failure

def require_auth(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_db_connected and os.environ.get('IN_TEST_MODE') != 'True':
            # This check prevents API calls if the real DB connection failed in production
            return jsonify({'message': 'Service Unavailable: Database connection failed.'}), 503

        if 'user_id' not in session:
            # Check for unauthorized access
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Check if user exists (to prevent stale sessions if user was deleted)
        if users_collection.find_one({'_id': session['user_id']}) is None:
            session.pop('user_id', None)
            return jsonify({'message': 'Unauthorized: User not found'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# --- User Authentication and Session Routes ---

@app.route('/api/signup', methods=['POST'])
def signup():
    # ... (Signup logic remains the same) ...
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not all([email, password, username]):
        return jsonify({'message': 'Missing fields'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 409
    
    # Password strength check (optional, but good practice)
    strength_result = zxcvbn(password)
    if strength_result['score'] < 3:
        return jsonify({'message': 'Password is too weak. Score: {strength_result["score"]}'}), 400

    hashed_password = generate_password_hash(password)
    
    # Insert new user
    user_id = users_collection.insert_one({
        'email': email,
        'username': username,
        'password_hash': hashed_password,
        'created_at': datetime.utcnow()
    }).inserted_id

    # Establish session
    session['user_id'] = str(user_id)
    
    # Prepare response cookie (Flask handles session cookie automatically)
    return jsonify({'message': 'User created and logged in successfully', 'username': username}), 201


@app.route('/api/login', methods=['POST'])
def login():
    # ... (Login logic remains the same) ...
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'Missing email or password'}), 400

    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = str(user['_id'])
        return jsonify({
            'message': 'Login successful', 
            'email': user['email'], 
            'username': user['username']
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    response = make_response(jsonify({'message': 'Logout successful'}), 200)
    # Explicitly clear the session cookie
    response.set_cookie('session', '', expires=0, secure=True, httponly=True, samesite='None', domain=None)
    return response

# --- Password Management Routes ---

@app.route('/api/passwords', methods=['POST'])
@require_auth
def store_password():
    # ... (Store password logic remains the same) ...
    data = request.get_json()
    site_name = data.get('site_name')
    username = data.get('username')
    password = data.get('password')
    user_id = session.get('user_id')

    if not all([site_name, username, password]):
        return jsonify({'message': 'Missing fields in password entry'}), 400

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
    
    # IMPORTANT: The user_id is a string (from session), but the document IDs in passwords_collection 
    # are BSON ObjectIds (if user_id was stored as ObjectId).
    # Assuming user_id is stored as string in the password collection (as per `store_password` logic)
    
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


@app.route('/api/passwords/<password_id>', methods=['DELETE'])
@require_auth
def delete_password(password_id):
    """Deletes a password entry by its ID, restricted to the session user."""
    user_id = session.get('user_id')
    
    try:
        # Validate the password_id format to ensure it's a valid ObjectId string
        object_id = ObjectId(password_id)
    except InvalidId:
        # This handles the case where the ID is not a 12-byte or 24-hex string
        return jsonify({'message': 'Invalid password ID format'}), 400
        
    # Perform the deletion: match by _id (ObjectId) AND user_id (string)
    result = passwords_collection.delete_one({
        '_id': object_id,
        'user_id': user_id
    })
    
    if result.deleted_count == 1:
        return jsonify({'message': 'Password deleted successfully'}), 200
    else:
        # This covers two cases: 
        # 1. The ID was valid but not found in the DB.
        # 2. The ID was valid but belonged to another user (access denied).
        return jsonify({'message': 'Password not found or access denied'}), 404


# --- Error Handling ---

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'message': 'Resource not found'}), 404


if __name__ == '__main__':
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        app.config['SECRET_KEY'] = 'default_secret_key_for_local_testing_32bytes' # Needed for Fernet key
    
    # Set IN_TEST_MODE to differentiate real startup from test execution (optional, but helpful)
    os.environ['IN_TEST_MODE'] = 'False'

    if not is_db_connected:
        print("FATAL: MongoDB not connected. Application will not function correctly without a real connection.")

    app.run(debug=True)