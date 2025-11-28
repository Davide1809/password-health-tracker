import os
import secrets
import json
import re
from datetime import datetime, timedelta
from functools import wraps 

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
# We rely on Pytest/monkeypatching to replace this import during testing
from pymongo import MongoClient 
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 
from bson.objectid import ObjectId 
import base64
from pymongo.errors import ConnectionFailure
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
    SECRET_KEY=app.config['SECRET_KEY'] if app.config['SECRET_KEY'] else secrets.token_urlsafe(32)
)

# Allow CORS only from the frontend URL, and allow credentials (cookies)
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

# --- Database Setup (MongoDB) ---

# CRITICAL FIX: The app now always imports MongoClient. 
# The test file (test_app.py) will use monkeypatch to replace MongoClient 
# with MockMongoClient before tests start, preventing live connection attempts during build.
client = MongoClient(MONGO_URI)

db = client.password_health_tracker
users_collection = db.users
passwords_collection = db.passwords 

# Ensure indices are created only if we are using a real MongoDB client and not testing
if not app.config.get('TESTING'):
    try:
        users_collection.create_index('email', unique=True)
        passwords_collection.create_index('user_id')
        client.admin.command('ping')
        print("Successfully connected to MongoDB.")
    except ConnectionFailure as e:
        print(f"ERROR: Could not connect to MongoDB: {e}")
    except Exception as e:
        # Handle cases where the mock client might not have admin.command
        pass


# --- Encryption Setup ---

FERNET_KEY_BASE64 = os.environ.get('FERNET_KEY')

if FERNET_KEY_BASE64:
    fernet = Fernet(FERNET_KEY_BASE64)
else:
    # Use a fixed, deterministic key for the mock/testing environment
    fixed_test_key = 'WjVUNjF0cThxV0h2Skt1NnB6SGV0ZGFyVjZ2ZkFhVks='
    fernet = Fernet(fixed_test_key)
    print("WARNING: FERNET_KEY is missing. Using a placeholder key.")


def encrypt_data(data):
    """Encrypts a string using Fernet."""
    if not isinstance(data, str):
        data = str(data)
    return fernet.encrypt(data.encode('utf-8'))

def decrypt_data(token):
    """Decrypts a Fernet token."""
    # Ensure token is bytes
    if isinstance(token, str):
        token = token.encode('utf-8')
    try:
        return fernet.decrypt(token).decode('utf-8')
    except Exception as e:
        print(f"Decryption failed: {e}")
        return "[Decryption Error]"


# --- Authentication Decorator ---
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized access: Session required.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'Password Health Tracker Backend'}), 200


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({'message': 'Invalid JSON or missing data.'}), 400

    email = data.get('email')
    password = data.get('password')
    user_name = data.get('user_name', email.split('@')[0] if email else 'User') 

    if not email or not password:
        return jsonify({'message': 'Missing email or password.'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'message': 'Invalid email format.'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists.'}), 409

    if len(password) < 8:
        return jsonify({'message': 'Password must be at least 8 characters long.'}), 400

    password_hash = generate_password_hash(password)

    user_data = {
        'email': email,
        'user_name': user_name,
        'password_hash': password_hash,
        'created_at': datetime.utcnow()
    }
    users_collection.insert_one(user_data)
    
    return jsonify({'message': 'User created successfully.', 'user_email': email}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({'message': 'Invalid JSON or missing data.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password.'}), 400

    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = str(user['_id']) 
        session['user_email'] = email
        
        return jsonify({
            'message': 'Login successful.',
            'user_email': email,
            'user_name': user.get('user_name', email.split('@')[0])
        }), 200
    
    return jsonify({'message': 'Invalid credentials.'}), 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    response = make_response(jsonify({'message': 'Logout successful.'}), 200)
    return response

@app.route('/api/passwords', methods=['POST'])
@require_auth
def save_password():
    user_id = session.get('user_id')
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'message': 'Invalid JSON or missing data.'}), 400
    
    site_name = data.get('site_name')
    username = data.get('username')
    password = data.get('password')

    if not all([site_name, username, password]):
        return jsonify({'message': 'Missing site name, username, or password.'}), 400

    # Ensure the encrypted data is stored as a decodable string representation
    encrypted_password_bytes = encrypt_data(password)
    
    password_entry = {
        'user_id': user_id,
        'site_name': site_name,
        'username': username,
        # Store as base64 string for easier storage/retrieval in BSON/JSON context
        'encrypted_password': encrypted_password_bytes.decode('utf-8'),
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

@app.route('/api/passwords/<password_id>', methods=['DELETE'])
@require_auth
def delete_password(password_id):
    user_id = session.get('user_id')
    
    try:
        password_object_id = ObjectId(password_id)
    except InvalidId:
        return jsonify({'message': 'Invalid password ID format.'}), 400 

    result = passwords_collection.delete_one({
        '_id': password_object_id,
        'user_id': user_id
    })

    if result.deleted_count == 0:
        return jsonify({'message': 'Password not found or unauthorized.'}), 404
        
    return jsonify({'message': 'Password deleted successfully.'}), 200


# --- Error Handling ---

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({'message': 'Resource not found'}), 404


if __name__ == '__main__':
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        app.config['SECRET_KEY'] = 'default_secret_key_for_testing'
    
    app.run(host='0.0.0.0', port=5000, debug=True)