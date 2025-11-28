import pytest
import json
import os
import sys
import base64
import mongomock

# --- CRITICAL FIX 1: Ensure 'backend' package is discoverable ---
# Add the project root (the directory containing the 'backend' folder) to the Python path.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- CRITICAL FIX 2: Correct Module Name ---
import backend.app as main_app 

# =================================================================
# FIX: Mocking Setup - Changed scope to 'function'
# =================================================================

@pytest.fixture(scope='function')
def mock_database_connection(monkeypatch):
    """
    Fixture to replace the real MongoDB connection with an in-memory mock.
    Scope is set to function to allow the use of the 'monkeypatch' fixture.
    """
    # print("Setting up MongoDB Mock...")
    # 1. Create a mock client and database
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.password_health_tracker
    
    # 2. Use monkeypatch to replace the global client and collections 
    #    in the main app module with the mock objects.
    monkeypatch.setattr(main_app, 'client', mock_client)
    monkeypatch.setattr(main_app, 'db', mock_db)
    monkeypatch.setattr(main_app, 'users_collection', mock_db.users)
    monkeypatch.setattr(main_app, 'passwords_collection', mock_db.passwords)
    # print("MongoDB Mock Setup Complete.")

@pytest.fixture
def client(mock_database_connection):
    """
    Test client fixture configured for Flask testing.
    Depends on 'mock_database_connection' to ensure the database is mocked first.
    """
    
    # 1. Configure the Flask app for testing
    main_app.app.config['TESTING'] = True
    
    # 2. Set environment variables required by app.py for test context
    os.environ['MONGO_URI'] = 'mongodb://mock/test_db' 
    os.environ['FRONTEND_URL'] = 'http://test.com'
    
    # 3. Use a deterministic key for testing the encryption/decryption logic
    test_secret = 'a_very_secure_test_secret_key_that_is_long_enough'
    os.environ['SECRET_KEY'] = test_secret
    
    # 4. Re-initialize the Fernet key object in the main app module after patching the environment
    #    This is necessary to ensure the Fernet object uses the test_secret key for decryption in tests.
    try:
        main_app.app.config['SECRET_KEY'] = test_secret
        
        # Now that get_fernet_key is defined in main_app, we can call it here.
        main_app.ENCRYPTION_KEY = main_app.get_fernet_key(test_secret)
        main_app.fernet = main_app.Fernet(main_app.ENCRYPTION_KEY)
        
    except Exception as e:
        # This error handling is now safe and primarily for debugging.
        print(f"Error during test Fernet key re-initialization: {e}")
        
    
    with main_app.app.test_client() as client:
        # 5. Clear the mock collections before each test run for isolation
        if hasattr(main_app, 'users_collection') and main_app.users_collection is not None:
            main_app.users_collection.delete_many({})
        if hasattr(main_app, 'passwords_collection') and main_app.passwords_collection is not None:
            main_app.passwords_collection.delete_many({})
            
        yield client

# --- Helper function for integration test setup ---
def register_test_user(client, email='test@example.com', password='Password123'):
    """Helper to simulate a user registration request."""
    return client.post(
        '/api/signup',
        data=json.dumps({'email': email, 'password': password}),
        content_type='application/json'
    )

# =================================================================
# Integration Tests (Requires Mock Database)
# =================================================================

def test_signup_successful(client):
    """Test user registration via the API."""
    response = register_test_user(client)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'User created' in data['message']
    
    # Check if user exists in mock DB
    user = main_app.users_collection.find_one({'email': 'test@example.com'})
    assert user is not None
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

def test_analyze_password_successful(client):
    """Test successful password analysis (mocked zxcvbn) without auth required."""
    # This test should now pass because @require_auth was removed from /api/analyze in app.py
    response = client.post(
        '/api/analyze',
        data=json.dumps({'password': 'AStrongPassword123!'}),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'score' in data
    # zxcvbn returns max score 4 for a strong password
    assert data['score'] == 4 
    
def test_password_management_flow(client):
    """Test saving and retrieving passwords."""
    # 1. Login to establish session
    register_test_user(client)
    login_response = client.post(
        '/api/login',
        data=json.dumps({'email': 'test@example.com', 'password': 'Password123'}),
        content_type='application/json'
    )
    # Ensure login was successful and we have a valid session/cookie
    assert login_response.status_code == 200
    
    # 2. Save a password
    save_data = {
        'site_name': 'MySocialMedia',
        'username': 'testuser',
        'password': 'SecretPassword42'
    }
    save_response = client.post(
        '/api/passwords',
        data=json.dumps(save_data),
        content_type='application/json'
    )
    assert save_response.status_code == 201
    
    # 3. Retrieve passwords
    get_response = client.get('/api/passwords')
    assert get_response.status_code == 200
    passwords = json.loads(get_response.data)
    
    assert len(passwords) == 1
    stored_password = passwords[0]
    
    # Check decryption worked and data integrity
    assert stored_password['site_name'] == 'MySocialMedia'
    assert stored_password['username'] == 'testuser'
    assert stored_password['password'] == 'SecretPassword42'