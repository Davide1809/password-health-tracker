import pytest
import json
import mongomock
from bson.objectid import ObjectId

# Import the main app module
import app

# --- Pytest Fixtures ---

# This fixture MUST run first and automatically to patch the MongoDB connection.
@pytest.fixture(scope="session", autouse=True)
def mock_mongo_client(monkeypatch):
    """
    Patches the real pymongo.MongoClient with the in-memory mongomock.MongoClient 
    before the app module is imported and initialized. This prevents any network 
    connection attempts during testing.
    """
    # 1. Replace the MongoClient import in the app module's namespace
    monkeypatch.setattr('app.MongoClient', mongomock.MongoClient)
    
    # 2. Force the app to use the TESTING flag
    app.app.config['TESTING'] = True
    
    # 3. Re-initialize the client within the app module after patching
    # This ensures that app.client uses the MockMongoClient now.
    # Note: We pass a fake URI since MockMongoClient accepts it but ignores it.
    app.client = app.MongoClient('mongodb://mockdb:27017/testdb')
    app.db = app.client.password_health_tracker
    app.users_collection = app.db.users
    app.passwords_collection = app.db.passwords
    
    # Yield control to the tests
    yield
    
    # Cleanup (though mongomock instances are usually ephemeral)
    app.users_collection.delete_many({})
    app.passwords_collection.delete_many({})


# Helper to get the authenticated user ID for the test session
def get_user_id(client):
    """Retrieves the user_id from the session cookie after login."""
    # Find the user inserted during the test run
    user = app.users_collection.find_one({'email': 'testuser@example.com'})
    return str(user['_id']) if user else None


# Fixture to provide the Flask test client
@pytest.fixture
def client():
    # Note: TESTING flag is already set in mock_mongo_client fixture
    app.app.config['SESSION_COOKIE_SECURE'] = False
    app.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
    with app.app.test_client() as client:
        yield client

# Fixture to clear the database before each test
@pytest.fixture(autouse=True)
def clean_db():
    app.users_collection.delete_many({})
    app.passwords_collection.delete_many({})
    # The yield allows the test to run, and the cleanup happens after
    yield

# --- Helper Functions for Tests ---

def register_test_user(client, email='testuser@example.com', password='StrongPassword123!'):
    """Helper to register a user."""
    user_data = {
        'email': email,
        'password': password,
        'user_name': 'TestUser' 
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

# --- Actual Tests ---

def test_root_path(client):
    """Test the basic health check path."""
    response = client.get('/')
    assert response.status_code == 200
    assert json.loads(response.data)['status'] == 'ok'

def test_signup_successful(client):
    """Test user registration via the API."""
    response = register_test_user(client)
    assert response.status_code == 201

def test_login_successful(client):
    """Test user login after successful signup."""
    register_test_user(client) 
    response = login_test_user(client)
    assert response.status_code == 200

def test_password_management_flow(client):
    """Test saving and retrieving passwords."""
    # 1. Login to establish session
    register_test_user(client)
    login_response = login_test_user(client)
    assert login_response.status_code == 200

    # 2. Save a password
    test_password = 'ComplexPassword123!'
    save_data = {
        'site_name': 'TestSite',
        'username': 'testuser',
        'password': test_password
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
    # Check that the decrypted password matches the original one
    assert retrieved_password['password'] == test_password 
    assert 'id' in retrieved_password

def test_get_passwords_empty(client):
    """Test retrieving passwords when the user has none."""
    register_test_user(client)
    login_test_user(client)

    get_response = client.get('/api/passwords')
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
    passwords = json.loads(get_response.data)
    
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
    assert delete_response.status_code == 400
    assert 'Invalid password ID format.' in delete_response.get_data(as_text=True)

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
    assert response.status_code == 401
    assert 'Invalid credentials.' in response.get_data(as_text=True)

def test_login_non_existent_user(client):
    """Test login failure for a user that hasn't signed up."""
    response = login_test_user(client, email='nonexistent@example.com')
    assert response.status_code == 401
    assert 'Invalid credentials.' in response.get_data(as_text=True)