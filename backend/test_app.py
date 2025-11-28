import pytest
import json
import os
import sys
import base64
import mongomock
from bson.objectid import ObjectId

# --- CRITICAL FIX: Direct Local Import ---
# Since test_app.py is in the same directory as app.py, 
# we use a direct import to avoid package resolution issues 
# when pytest is run from the 'backend' directory.
import app as main_app 

# =================================================================
# Mocking Setup 
# =================================================================

@pytest.fixture(scope='function')
def mock_database_connection(monkeypatch):
    """
    Fixture to replace the real MongoDB connection with an in-memory mock.
    """
    # 1. Create a mock client and database
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.password_health_tracker
    
    # 2. Use monkeypatch to replace the global client and collections 
    #    in the main app module with the mock objects.
    monkeypatch.setattr(main_app, 'client', mock_client)
    monkeypatch.setattr(main_app, 'db', mock_db)
    monkeypatch.setattr(main_app, 'users_collection', mock_db.users)
    monkeypatch.setattr(main_app, 'passwords_collection', mock_db.passwords)

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
    try:
        main_app.app.config['SECRET_KEY'] = test_secret
        # Need to use main_app.get_fernet_key since it's defined in app.py
        main_app.ENCRYPTION_KEY = main_app.get_fernet_key(test_secret)
        main_app.fernet = main_app.Fernet(main_app.ENCRYPTION_KEY)
    except Exception as e:
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
# Tests
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

def test_delete_password_successful(client):
    """Test successful deletion of a password."""
    # 1. Login
    register_test_user(client)
    client.post('/api/login', data=json.dumps({'email': 'test@example.com', 'password': 'Password123'}), content_type='application/json')
    
    # 2. Save a password
    save_data = {
        'site_name': 'ToDelete',
        'username': 'tempuser',
        'password': 'tempPassword'
    }
    client.post('/api/passwords', data=json.dumps(save_data), content_type='application/json')
    
    # 3. Get the ID of the saved password
    get_response = client.get('/api/passwords')
    passwords = json.loads(get_response.data)
    password_id = passwords[0]['id']
    
    # 4. Delete the password
    delete_response = client.delete(f'/api/passwords/{password_id}')
    assert delete_response.status_code == 200
    
    # 5. Verify deletion
    verify_response = client.get('/api/passwords')
    verify_passwords = json.loads(verify_response.data)
    assert len(verify_passwords) == 0

def test_delete_password_invalid_id(client):
    """Test deletion with an invalid ID format."""
    # 1. Login
    register_test_user(client)
    client.post('/api/login', data=json.dumps({'email': 'test@example.com', 'password': 'Password123'}), content_type='application/json')
    
    # 2. Attempt deletion with a non-ObjectId string
    delete_response = client.delete('/api/passwords/invalid_id_format')
    assert delete_response.status_code == 400
    data = json.loads(delete_response.data)
    assert 'Invalid password ID format' in data['message']

def test_delete_password_unauthorized(client):
    """Test deletion when not logged in."""
    # Attempt to delete without logging in
    delete_response = client.delete('/api/passwords/some_id_placeholder')
    assert delete_response.status_code == 401
    data = json.loads(delete_response.data)
    assert 'Unauthorized' in data['message']