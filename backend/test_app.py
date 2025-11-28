import pytest
import json
import os
from mongomock import MongoClient as MockMongoClient
from unittest.mock import patch, MagicMock

# --- Helper function for tests ---

def register_test_user(client, email='test@example.com', password='Password123', username='TestUser'):
    """Helper to perform a user registration API call."""
    return client.post(
        '/api/signup',
        data=json.dumps({'email': email, 'password': password, 'username': username}),
        content_type='application/json'
    )

def login_test_user(client, email='test@example.com', password='Password123'):
    """Helper to perform a user login API call."""
    return client.post(
        '/api/login',
        data=json.dumps({'email': email, 'password': password}),
        content_type='application/json'
    )

# --- Pytest Fixture (CRITICAL FIX) ---

@pytest.fixture
def client(monkeypatch):
    """
    Configures the Flask test client and mocks the MongoDB connection using mongomock.

    This prevents the Flask app from failing during initialization due to a missing 
    or invalid MONGO_URI, which was causing the 503 SERVICE UNAVAILABLE errors.
    """
    
    # 1. Mock the environment variables needed by the app
    # Set IN_TEST_MODE to True so the app logic can adjust if needed
    monkeypatch.setenv("IN_TEST_MODE", "True") 
    monkeypatch.setenv("SECRET_KEY", "test_secret_key_for_test_environment")
    monkeypatch.setenv("MONGO_URI", "mongodb://mock:27017/testdb")
    
    # 2. Mock the real pymongo.MongoClient with the mongomock client
    def mock_mongo_client(*args, **kwargs):
        # Create a mock client instance and force the app to think the connection succeeded
        mock_client = MockMongoClient()
        # Mock the admin command to ensure the connection health check passes
        mock_client.admin.command = MagicMock(return_value={'ok': 1.0})
        return mock_client

    monkeypatch.setattr("pymongo.MongoClient", mock_mongo_client)

    # 3. Import the application after mocking is complete
    # This ensures that the app's initialization uses the mock client
    from app import app
    
    # Resetting the DB is good practice for isolated tests
    app.config['TESTING'] = True
    
    # 4. Correct the app's internal DB status after mocking
    # Since we mocked the client, we manually set the flag the app uses
    app.is_db_connected = True 

    # 5. Use the Flask test client
    with app.test_client() as client:
        yield client


# --- Test Cases ---

def test_root_path(client):
    """Test the basic health check path."""
    response = client.get('/')
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Welcome to the Password Health API'

# Fix 1: 503 -> 201
def test_signup_successful(client):
    """Test user registration via the API."""
    response = register_test_user(client)
    assert response.status_code == 201

# Fix 2: 503 -> 200
def test_login_successful(client):
    """Test user login after successful signup."""
    register_test_user(client) # Signup first
    
    # Now log in
    response = login_test_user(client)

    assert response.status_code == 200
    assert 'Login successful' in json.loads(response.data)['message']

def test_login_unsuccessful(client):
    """Test login with incorrect password."""
    register_test_user(client)
    response = client.post(
        '/api/login',
        data=json.dumps({'email': 'test@example.com', 'password': 'WrongPassword'}),
        content_type='application/json'
    )
    assert response.status_code == 401
    assert 'Invalid credentials' in json.loads(response.data)['message']

# Fix 3: 503 -> 200
def test_password_management_flow(client):
    """Test saving and retrieving passwords."""
    # 1. Login to establish session
    register_test_user(client)
    login_response = login_test_user(client)

    # Ensure login was successful and we have a valid session/cookie
    assert login_response.status_code == 200

    # 2. Save a password
    save_data = {
        'site_name': 'TestSite',
        'username': 'testuser',
        'password': 'StrongPassword123!'
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

    # Check if the saved password is in the retrieved list
    assert len(passwords) == 1
    assert passwords[0]['site_name'] == 'TestSite'
    assert passwords[0]['password'] == 'StrongPassword123!' # Check decryption

def test_get_passwords_empty(client):
    """Test retrieving passwords when the user has none."""
    register_test_user(client)
    login_test_user(client)
    
    get_response = client.get('/api/passwords')
    assert get_response.status_code == 200
    assert len(json.loads(get_response.data)) == 0

# Fix 4: KeyError: 0 (now relies on the flow above being fixed)
def test_delete_password_successful(client):
    """Test successful deletion of a password."""
    # 1. Login
    register_test_user(client)
    login_test_user(client)

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
    
    # CRITICAL: This was failing before because get_response was 503
    assert len(passwords) == 1
    password_id = passwords[0]['id']

    # 4. Delete the password
    delete_response = client.delete(f'/api/passwords/{password_id}')
    assert delete_response.status_code == 200
    assert 'deleted successfully' in json.loads(delete_response.data)['message']

    # 5. Verify deletion
    get_response_after = client.get('/api/passwords')
    assert len(json.loads(get_response_after.data)) == 0

# Fix 5: 503 -> 400
def test_delete_password_invalid_id(client):
    """Test deletion with an invalid ID format."""
    # 1. Login
    register_test_user(client)
    login_test_user(client)

    # 2. Attempt deletion with a non-ObjectId string
    # The backend (app.py) should now return 400 due to InvalidId handling
    delete_response = client.delete('/api/passwords/invalid_id_format')
    assert delete_response.status_code == 400
    assert 'Invalid password ID format' in json.loads(delete_response.data)['message']

# Fix 6: 503 -> 401
def test_delete_password_unauthorized(client):
    """Test deletion when not logged in."""
    # Attempt to delete without logging in
    # Use a dummy but valid looking ID to test the 401 (unauthorized) first
    delete_response = client.delete('/api/passwords/60f4c3c3a2a6b2a0c4f8b2c2')
    assert delete_response.status_code == 401