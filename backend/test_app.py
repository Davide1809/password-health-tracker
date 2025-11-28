import pytest
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash # Import hashing functions from Werkzeug
from app import app, users_collection, passwords_collection # Assuming app and collections are exported by app.py

# Set up a test client
@pytest.fixture
def client():
    # Use test configuration
    app.config['TESTING'] = True
    # Ensure no cookies are sent during tests (if you want to test unauthenticated access)
    # or handle cookies specifically in tests if required.
    
    # We must mock the environment variables that are checked in app.py's __main__ block
    os.environ['SECRET_KEY'] = 'test_secret_key'
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
    os.environ['ENCRYPTION_KEY'] = 'a' * 43 # Dummy key for Fernet initialization
    
    with app.test_client() as client:
        # Clear the database before each test run (CRITICAL for isolated tests)
        users_collection.delete_many({})
        passwords_collection.delete_many({})
        yield client

# --- Helper function for test setup (if needed) ---
def register_test_user(client, email='test@example.com', password='Password123'):
    return client.post(
        '/api/signup',
        data=json.dumps({'email': email, 'password': password}),
        content_type='application/json'
    )

# --- Test Cases ---

def test_signup_successful(client):
    """Test user registration."""
    response = register_test_user(client)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'User created' in data['message']
    
    # Check if user exists in DB
    user = users_collection.find_one({'email': 'test@example.com'})
    assert user is not None
    # Check if the session was created
    assert 'Set-Cookie' in response.headers

def test_login_successful(client):
    """Test user login after successful signup."""
    register_test_user(client) # Signup first
    
    # Now log in
    response = client.post(
        '/api/login',
        data=json.dumps({'email': 'test@example.com', 'password': 'Password123'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Login successful' in data['message']
    assert 'Set-Cookie' in response.headers

def test_analyze_password_requires_auth(client):
    """Test that password analysis is protected."""
    # Attempt to analyze without logging in
    response = client.post(
        '/api/analyze',
        data=json.dumps({'password': 'weak'}),
        content_type='application/json'
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Authentication required' in data['message']

def test_analyze_password_successful(client):
    """Test successful password analysis after login."""
    register_test_user(client) # Log in
    
    # Analyze a password
    response = client.post(
        '/api/analyze',
        data=json.dumps({'password': 'AStrongPassword123!'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'score' in data
    assert data['score'] == 4 # A strong password should get a score of 4
    
# Add more tests for add_password, get_passwords, and logout routes here...