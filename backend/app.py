import os
import json
import re
from datetime import datetime, timedelta
from functools import wraps
from bson.objectid import ObjectId

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet, InvalidToken # Imported InvalidToken
from zxcvbn import zxcvbn 
import base64

# --- Configuration and Initialization ---
# The application object MUST be defined before any configuration is applied.
app = Flask(__name__)

# Load environment variables (set during gcloud deploy)
SECRET_KEY_ENV = os.environ.get('SECRET_KEY')
MONGO_URI = os.environ.get('MONGO_URI')

# *** STARTUP SANITY CHECK LOGGING (NEW) ***
# We check if the critical environment variables are loaded from the environment
if SECRET_KEY_ENV and MONGO_URI:
    # Print success message, only showing the length of the keys for security
    print(f"CRITICAL SANITY CHECK: Keys Found! SECRET_KEY length: {len(SECRET_KEY_ENV)}, MONGO_URI status: Found.")
else:
    # Print failure message clearly
    print(f"CRITICAL SANITY CHECK: FAILED TO LOAD ENVIRONMENT VARIABLES.")
    if not SECRET_KEY_ENV:
        print("FATAL ERROR: SECRET_KEY is missing from environment variables.")
    if not MONGO_URI:
        print("FATAL ERROR: MONGO_URI is missing from environment variables.")
# *** END SANITY CHECK LOGGING ***

app.config['SECRET_KEY'] = SECRET_KEY_ENV

# Configure session cookies for secure cross-site interaction
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
)

# Allow CORS only from the frontend URL, and allow credentials (cookies)
CORS(app, supports_credentials=True, origins=['https://password-frontend-749522457256.web.app']) # Assuming this is your frontend URL

# --- Database Setup (MongoDB) ---
client = None
db = None
users_collection = None
passwords_collection = None

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping') # Try to ping the database immediately
        db = client.password_health_tracker
        users_collection = db.users
        passwords_collection = db.passwords 
        print("Successfully connected to MongoDB.")
    else:
        print("WARNING: MONGO_URI not set. Database operations will fail.")
except Exception as e:
    print(f"FATAL: Error connecting to MongoDB at startup: {e}")
    # Collections remain None if connection fails

# --- Encryption Setup ---
# Derive encryption key from SECRET_KEY for Fernet. 
def get_fernet_key(secret_key):
    import hashlib
    key_hash = hashlib.sha256(secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key_hash[:32])

# Initialize Fernet instance
FERNET_KEY = None
fernet = None
if app.config['SECRET_KEY']:
    FERNET_KEY = get_fernet_key(app.config['SECRET_KEY'])
    fernet = Fernet(FERNET_KEY)
else:
    # Use a dummy key if running without a real secret key
    fernet = Fernet(b'default_fernets_key_for_testing_00') 
    print("WARNING: Using default Fernet key. Check SECRET_KEY environment variable.")


def encrypt_data(data):
    """Encrypts a string using Fernet."""
    if not fernet:
        # This shouldn't happen if initialization above is correct, but safe check
        raise RuntimeError("Fernet encryption key not initialized.")
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(data):
    """
    Decrypts a Fernet token string. 
    Handles InvalidToken exception which often points to a key mismatch.
    """
    if not fernet:
        raise RuntimeError("Fernet encryption key not initialized.")
    
    if not isinstance(data, str) or not data:
         print(f"CRITICAL DECRYPTION ERROR: Input data is invalid or empty: {data}")
         return "[Decryption Error: Invalid Data Type or Empty String]"

    try:
        return fernet.decrypt(data.encode()).decode()
    except InvalidToken:
        print("CRITICAL DECRYPTION ERROR: Invalid token detected. Key mismatch or data corruption.")
        return "[Decryption Error: Invalid Key/Token]"
    except Exception as e:
        print(f"Decryption error (General): {e}. Malformed token: {data[:30]}...")
        return "[Decryption Error: General Failure]"

# --- Authentication Decorator ---

def require_auth(f):
    """Decorator to ensure the user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Unauthorized. Please log in.'}), 401
        
        # Check if database collections are initialized
        if passwords_collection is None or users_collection is None:
            print("FATAL: Database connection failed. Denying request.")
            return jsonify({'message': 'Server is currently experiencing database issues. Please try again later.'}), 503
            
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

# --- DEBUGGING ROUTE ---
@app.route('/api/session-status', methods=['GET'])
def session_status():
    """Returns the current user session status for debugging."""
    if 'user_id' in session:
        return jsonify({
            'status': 'Authenticated',
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name')
        }), 200
    else:
        return jsonify({
            'status': 'Not Authenticated',
            'message': 'No active user session found.'
        }), 200
# --- END DEBUGGING ROUTE ---


@app.route('/api/signup', methods=['POST'])
def signup():
    # If this fails, the DB connection failed during startup
    if users_collection is None:
        return jsonify({'message': 'Server is currently experiencing database issues.'}), 503
        
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_name = data.get('user_name') 

    # If the request fails before here, the issue is ENV variables or network.
    
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
    if users_collection is None:
        return jsonify({'message': 'Server is currently experiencing database issues.'}), 503

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'Missing required fields.'}), 400

    # 1. Find user
    user = users_collection.find_one({'email': email})

    # 2. Verify password
    password_hash = user.get('password_hash') if user else None

    if user and password_hash and check_password_hash(password_hash, password):
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
    """
    if 'user_id' in session:
        session.clear()
        
    # Create a response object
    response = make_response(jsonify({'message': 'Logout successful. Session cleared.'}), 200)
    
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
    
    try:
        # Encrypt the sensitive password data before storing
        encrypted_password = encrypt_data(password)
    except RuntimeError as e:
        print(f"Encryption setup error: {e}")
        return jsonify({'message': 'Server encryption setup failed.'}), 500

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
    
    try:
        # Retrieve passwords for the current user, sorted by creation date (newest first)
        cursor = passwords_collection.find({'user_id': user_id}).sort('created_at', -1)
    
        passwords_list = []
        
        for doc in cursor:
            encrypted_data = doc.get('encrypted_password')
            
            if not encrypted_data or not isinstance(encrypted_data, str):
                print(f"SEVERE WARNING: Document with ID {doc['_id']} is missing 'encrypted_password' field or it is not a string. Skipping document.")
                continue 
                
            decrypted_password = decrypt_data(encrypted_data)
            
            if "[Decryption Error: Invalid Key/Token]" in decrypted_password:
                 print("Aborting password retrieval due to critical decryption failure.")
                 return jsonify({
                     'message': 'Critical error: Failed to decrypt stored passwords. The encryption key may have changed since the data was stored. Please contact support.'
                 }), 500
            
            if "[Decryption Error: General Failure]" in decrypted_password or "[Decryption Error: Invalid Data Type or Empty String]" in decrypted_password:
                 print(f"General decryption failure for document {doc['_id']}. Showing placeholder.")
                 decrypted_password = "[Decryption Failed]"
            
            passwords_list.append({
                'id': str(doc['_id']),
                'site_name': doc['site_name'],
                'username': doc['username'],
                'password': decrypted_password, 
                'created_at': doc['created_at'].isoformat()
            })
            
        return jsonify(passwords_list), 200

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"FATAL UNHANDLED EXCEPTION IN get_passwords: {e}")
        print(f"TRACEBACK: {error_traceback}")
        
        return jsonify({'message': 'Internal Server Error: Failed to process passwords list due to an unexpected exception. Check server logs for full details.'}), 500


@app.route('/api/passwords/<password_id>', methods=['DELETE'])
@require_auth
def delete_password(password_id):
    user_id = session.get('user_id')

    if not ObjectId.is_valid(password_id):
        return jsonify({'message': 'Invalid password ID format.'}), 400

    obj_id = ObjectId(password_id)

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
    # This block usually runs only in local development, but good practice to check if it's triggering
    if not all(os.environ.get(k) for k in ['SECRET_KEY', 'MONGO_URI']):
        print("WARNING: Running locally without required environment variables.")
        # Only set defaults if running locally AND they are not defined in the environment
        if not os.environ.get('SECRET_KEY'):
            app.config['SECRET_KEY'] = 'default_secret_key_for_local_dev_12345678'
        
        if not os.environ.get('MONGO_URI'):
            MONGO_URI = 'mongodb://localhost:27017/'
        
        # Re-check and set up Fernet key for local run if it wasn't set earlier due to missing env var
        if FERNET_KEY is None:
            new_fernet_key = get_fernet_key(app.config['SECRET_KEY'])
            FERNET_KEY = new_fernet_key
            fernet = Fernet(FERNET_KEY)

        # Re-initialize DB connection for local run
        if not os.environ.get('MONGO_URI') and MONGO_URI:
            try:
                client = MongoClient(MONGO_URI)
                db = client.password_health_tracker
                users_collection = db.users
                passwords_collection = db.passwords
                print("Connected to local MongoDB.")
            except Exception as e:
                print(f"Error connecting to local MongoDB: {e}")
             
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))