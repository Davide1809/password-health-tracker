import pytest
import json
from app import app, users_collection, passwords_collection
from bson.objectid import ObjectId
# Import MongoClient from mongomock if the environment is a test environment
# In this simulated environment, we assume the collections are correctly mocked.

# Mocking setup (assumed to be in the testing environment's setup phase)
# Note: I'm redefining this section to ensure the helpers are included.

# --- Helper Functions for Tests ---

def register_test_user(client, email='testuser@example.com', password='StrongPassword123!'):
    """Helper to register a user."""
    user_data = {
        'email': email,
        'password': password,
        'user_name': 'TestUser' # Ensure user_name is present (Fix for 400 signup error)
    }
    return client.post(
        '/api/signup', 
        data=json.dumps(user_data), 
        content_type='application/json'
    )

def login_test_user(client, email='testuser@example.com', password='StrongPassword123!'):
    """Helper to log in a user."""
    login_data = {
        'email': email,
        'password': password
    }
    return client.post(
        '/api/login', 
        data=json.dumps(login_data), 
        content_type='application/json'
    )

# --- Actual Tests (Remaining tests from the original file, ensured to match names) ---

# Fixture to clear the database before each test (assuming mongomock is used)
@pytest.fixture(autouse=True)
def clean_db():
    users_collection.delete_many({})
    passwords_collection.delete_many({})

# Flask test client fixture
@pytest.fixture
def client():
    # Set up the test client with app configuration
    app.config['TESTING'] = True
    # Relax cookie settings for testing environment
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
    with app.test_client() as client:
        yield client

def test_root_path(client):
    """Test the basic health check path."""
    response = client.get('/')
    # FIX: Expect 200 now that '/' route is implemented
    assert response.status_code == 200
    assert json.loads(response.data)['status'] == 'ok'

def test_signup_successful(client):
    """Test user registration via the API."""
    response = register_test_user(client)
    # FIX: Expect 201 Created
    assert response.status_code == 201

def test_login_successful(client):
    """Test user login after successful signup."""
    register_test_user(client) # Signup first
    
    # Now log in
    response = login_test_user(client)
    
    # FIX: Expect 200 now that session is correctly set in app.py
    assert response.status_code == 200

def test_password_management_flow(client):
    """Test saving and retrieving passwords."""
    # 1. Login to establish session
    register_test_user(client)
    login_response = login_test_user(client)
    
    # Assert login success (prerequisite, fixed by previous tests)
    assert login_response.status_code == 200

    # 2. Save a password
    save_data = {
        'site_name': 'TestSite',
        'username': 'testuser',
        'password': 'ComplexPassword123!'
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
    
    retrieved_password = passwords[0]
    assert retrieved_password['site_name'] == 'TestSite'
    assert retrieved_password['password'] == 'ComplexPassword123!' 
    assert 'id' in retrieved_password

def test_get_passwords_empty(client):
    """Test retrieving passwords when the user has none."""
    register_test_user(client)
    login_test_user(client)

    get_response = client.get('/api/passwords')
    # FIX: Expect 200 now that session is correctly set
    assert get_response.status_code == 200
    passwords = json.loads(get_response.data)
    assert len(passwords) == 0

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
    assert get_response.status_code == 200
    passwords = json.loads(get_response.data)
    
    # FIX: This now succeeds because the login and GET request succeed.
    assert len(passwords) == 1
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
    login_test_user(client)

    # 2. Attempt deletion with a non-ObjectId string
    delete_response = client.delete('/api/passwords/invalid_id_format')
    # FIX: Expect 400 now that the InvalidId handling is implemented in app.py
    assert delete_response.status_code == 400
    assert 'Invalid password ID format.' in delete_response.get_data(as_text=True)

# Add other expected tests that were successful previously
def test_password_strength_check(client):
    """Test that signup fails with a weak password (based on len < 8)."""
    weak_user_data = {
        'email': 'weak@example.com',
        'password': 'short',
        'user_name': 'WeakUser'
    }
    response = client.post(
        '/api/signup', 
        data=json.dumps(weak_user_data), 
        content_type='application/json'
    )
    assert response.status_code == 400
    assert 'Password must be at least 8 characters long.' in response.get_data(as_text=True)

def test_login_invalid_credentials(client):
    """Test login failure with bad password."""
    register_test_user(client)
    response = login_test_user(client, password='WrongPassword123!')
    # FIX: Expect 401 Unauthorized for bad credentials
    assert response.status_code == 401
    assert 'Invalid credentials.' in response.get_data(as_text=True)

def test_login_non_existent_user(client):
    """Test login failure for a user that hasn't signed up."""
    response = login_test_user(client, email='nonexistent@example.com')
    # FIX: Expect 401 Unauthorized
    assert response.status_code == 401
    assert 'Invalid credentials.' in response.get_data(as_text=True)