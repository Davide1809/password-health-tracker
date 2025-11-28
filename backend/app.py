import os
import secrets
import json
import re
from datetime import datetime, timedelta
from functools import wraps
import hashlib # NEW: For generating a stable Fernet key

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from zxcvbn import zxcvbn 
import base64
from dotenv import load_dotenv
from bson.objectid import ObjectId 

# Conditionally import mock client for testing environment
if os.environ.get('TESTING') == 'True':
    from mongomock import MongoClient as MockMongoClient

# Load environment variables from .env file (for local development)
load_dotenv()

# --- Configuration and Initialization ---
app = Flask(__name__)

# Load environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
MONGO_URI = os.environ.get('MONGO_URI')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Fallback for local testing if not set
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(32)
    print("WARNING: Using temporary SECRET_KEY for local testing.")
    
app.config['SECRET_KEY'] = SECRET_KEY

# Configure session cookies for secure cross-site interaction
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
    # Session is a browser-session cookie, expires when the browser is closed.
)

# Allow CORS only from the frontend URL, and allow credentials (cookies)
CORS(app, supports_credentials=True, origins=[FRONTEND_URL])

# --- Database Setup (MongoDB) ---
client = None
db = None
users_collection = None
passwords_collection = None
DB_CONNECTED = False

def initialize_db():
    """Initializes the MongoDB connection, using MockDB if in testing mode."""
    global client, db, users_collection, passwords_collection, DB_CONNECTED
    
    if os.environ.get('TESTING') == 'True':
        # FIX: Use mongomock for unit tests to prevent 503 errors.
        print("DB Initialization using MockMongoDB for testing.")
        client = MockMongoClient()
        db = client.password_health_tracker
        users_collection = db.users
        passwords_collection = db.passwords 
        DB_CONNECTED = True 
        return

    if not MONGO_URI:
        print("WARNING: MONGO_URI not set. Running without persistent database.")
        DB_CONNECTED = False
        return

    try:
        # Use a lightweight command to check the connection during initialization
        client = MongoClient(MONGO_URI)
        client.admin.command('ismaster') 
        db = client.password_health_tracker
        users_collection = db.users
        passwords_collection = db.passwords 
        DB_CONNECTED = True
        print("Successfully connected to MongoDB.")
        
    except Exception as e:
        print(f"ERROR: MongoDB connection failed at initialization: {e}")
        DB_CONNECTED = False

# Initialize DB on startup
initialize_db()

# Function to ensure DB is connected before an operation
def ensure_db_connection():
    """Returns an error response if the database is not connected, otherwise None."""
    if not DB_CONNECTED:
        return jsonify({'message': 'Database service unavailable.'}), 503
    return None

# --- Cryptography Setup (Fernet) ---

def get_fernet_key(secret_key):
    """Generates a secure Fernet key (32 bytes) from the Flask secret key using SHA256."""
    # FIX: Ensure the key is exactly 32 bytes (44 characters when B64-encoded) for Fernet
    # Hash the secret key to get exactly 32 bytes (256 bits)
    hash_bytes = hashlib.sha256(secret_key.encode('utf-8')).digest()
    
    # Base64 encode the 32 bytes to get the 44-character Fernet key
    fernet_key = base64.urlsafe_b64encode(hash_bytes)
    return fernet_key

try:
    ENCRYPTION_KEY = get_fernet_key(SECRET_KEY)
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"Error initializing Fernet: {e}")
    # Initialize Fernet with a dummy key for safety
    fernet = Fernet(Fernet.generate_key()) 

def encrypt_data(data):
    """Encrypts a string using Fernet."""
    encoded_data = data.encode('utf-8')
    return fernet.encrypt(encoded_data).decode('utf-8')

def decrypt_data(encrypted_data):
    """Decrypts a Fernet token into a string."""
    token = encrypted_data.encode('utf-8')
    try:
        decrypted_bytes = fernet.decrypt(token)
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return "[Decryption Failed]"

# --- Authentication Decorator ---

def require_auth(f):
    """Decorator to ensure user is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check DB Status
        db_check = ensure_db_connection()
        if db_check:
            return db_check

        # 2. Check Session
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({'message': 'Unauthorized. Please log in.'}), 401
        
        # 3. Check User Existence
        # Fetch only the _id if possible, more efficient
        user = users_collection.find_one({'_id': user_id}, {'_id': 1})
        if not user:
             # Clear session if user not found (e.g., user deleted)
            session.pop('user_id', None)
            session.modified = True # Ensure session is saved/updated immediately
            return jsonify({'message': 'Unauthorized. User not found.'}), 401

        return f(*args, **kwargs)
    return decorated_function

# --- User API Routes ---

@app.route('/api/status', methods=['GET'])
def status():
    """Check authentication status."""
    user_id = session.get('user_id')
    user_email = None
    user_name = None
    
    # Check if we need to query the database
    if user_id:
        db_check = ensure_db_connection()
        if db_check:
            # If DB is down but session exists, treat as logged in but warn on email
            user_email = "Database Unavailable"
            user_name = "DB Error"
        else:
            user = users_collection.find_one({'_id': user_id})
            if user:
                user_email = user['email']
                user_name = user.get('name', user['email'].split('@')[0])
            else:
                 # If user_id is in session but user not in DB, clear session
                session.pop('user_id', None)
                session.modified = True
                user_id = None # Set to None to reflect unauthenticated state
            
    return jsonify({
        'isAuthenticated': user_id is not None,
        'userEmail': user_email,
        'userName': user_name
    }), 200

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handle new user registration."""
    db_check = ensure_db_connection()
    if db_check:
        return db_check
        
    data = request.get_json()
    email = data.get('email').lower().strip()
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 409

    # Hash password securely
    hashed_password = generate_password_hash(password)

    user_data = {
        '_id': secrets.token_urlsafe(16),
        'email': email,
        'password': hashed_password,
        'created_at': datetime.utcnow()
    }

    try:
        users_collection.insert_one(user_data)
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return jsonify({'message': 'Failed to create user due to database error.'}), 500

    
    # Immediately log in the user upon successful signup
    session['user_id'] = user_data['_id']
    session.modified = True # CRITICAL FIX: Ensure the session is marked for saving
    
    # Create a response object to set the cookie
    response = make_response(jsonify({'message': 'User created and logged in.'}), 201)
    return response

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login."""
    db_check = ensure_db_connection()
    if db_check:
        return db_check

    data = request.get_json()
    email = data.get('email').lower().strip()
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400

    user = users_collection.find_one({'email': email})

    if user and check_password_hash(user['password'], password):
        # Set session cookie
        session['user_id'] = user['_id']
        session.modified = True # CRITICAL FIX: Ensure the session is marked for saving
        
        # Create a response object to set the cookie
        response = make_response(jsonify({'message': 'Login successful'}), 200)
        return response
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Handle user logout and session clearance."""
    session.pop('user_id', None)
    session.modified = True
    return jsonify({'message': 'Logged out successfully'}), 200

# --- Password Analysis Route ---

@app.route('/api/analyze', methods=['POST'])
def analyze_password():
    """Analyze a password using zxcvbn."""
    # Does not require DB connection or auth
    data = request.get_json()
    password = data.get('password', '')
    
    # zxcvbn computes the score (0-4) and other details
    analysis = zxcvbn(password)
    
    # Only return the relevant security score
    return jsonify({
        'score': analysis['score'],
        'feedback': analysis['feedback'],
        'crack_times_seconds': analysis['crack_times_seconds']
    }), 200

# --- Password Management Routes (Requires Auth) ---

@app.route('/api/passwords', methods=['POST'])
@require_auth
def store_password():
    """Store an encrypted password for the logged-in user."""
    # DB connection is checked in @require_auth
    data = request.get_json()
    user_id = session.get('user_id')
    site_name = data.get('site_name')
    username = data.get('username')
    password = data.get('password')

    if not all([site_name, username, password]):
        return jsonify({'message': 'Missing site name, username, or password'}), 400

    # Encrypt the password before storing
    encrypted_password = encrypt_data(password)

    password_entry = {
        'user_id': user_id,
        'site_name': site_name,
        'username': username,
        'encrypted_password': encrypted_password,
        'created_at': datetime.utcnow()
    }

    try:
        passwords_collection.insert_one(password_entry)
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return jsonify({'message': 'Failed to store password due to database error.'}), 500


    return jsonify({'message': 'Password stored securely.'}), 201


@app.route('/api/passwords', methods=['GET'])
@require_auth
def get_passwords():
    """Retrieve and decrypt all passwords for the logged-in user."""
    # DB connection is checked in @require_auth
    user_id = session.get('user_id')
    
    try:
        # Fetch passwords sorted by creation date (newest first)
        cursor = passwords_collection.find({'user_id': user_id}).sort('created_at', -1)
    except Exception as e:
        print(f"DB Find Error: {e}")
        return jsonify({'message': 'Failed to retrieve passwords due to database error.'}), 500
    
    passwords_list = []
    for doc in cursor:
        decrypted_password = decrypt_data(doc['encrypted_password'])
        
        # NOTE: Passwords must be converted to string before sending as JSON
        passwords_list.append({
            'id': str(doc['_id']),
            'site_name': doc['site_name'],
            'username': doc['username'],
            'password': decrypted_password, 
            'created_at': doc['created_at'].isoformat()
        })
        
    return jsonify(passwords_list), 200

@app.route('/api/passwords/<id>', methods=['DELETE'])
@require_auth
def delete_password(id):
    """Delete a password by its MongoDB ObjectID string ID."""
    # DB connection is checked in @require_auth
    user_id = session.get('user_id')

    try:
        # Check if the string ID can be converted to ObjectId
        if not ObjectId.is_valid(id):
            return jsonify({'message': 'Invalid password ID format'}), 400
            
        # Use ObjectId to correctly query MongoDB
        result = passwords_collection.delete_one({
            '_id': ObjectId(id),
            'user_id': user_id
        })
        
        if result.deleted_count == 1:
            return jsonify({'message': 'Password deleted successfully'}), 200
        else:
            return jsonify({'message': 'Password not found or unauthorized'}), 404

    except Exception as e:
        print(f"Error deleting password: {e}")
        return jsonify({'message': 'A database error occurred during deletion.'}), 500

# --- Error Handling ---

@app.errorhandler(404)
def resource_not_found(e):
    """Custom 404 handler."""
    return jsonify({'message': 'Resource not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Custom 405 handler."""
    return jsonify({'message': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 handler."""
    print(f"Internal Server Error: {e}")
    return jsonify({'message': 'Internal server error'}), 500


if __name__ == '__main__':
    # When running locally, Flask will use its default server configuration.
    app.run(debug=True, host='0.0.0.0', port=8080)