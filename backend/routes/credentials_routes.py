"""
Credentials management routes
"""
from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from models.credential import Credential

bp = Blueprint('credentials', __name__, url_prefix='/api/credentials')

# Get MongoDB instance (will be injected from app)
mongo = None

def set_mongo(mongo_instance):
    """Set the MongoDB instance for routes"""
    global mongo
    mongo = mongo_instance


def get_user_id_from_token(request_obj):
    """
    Extract user_id from JWT token in Authorization header
    
    Returns:
        str: user_id or None if token is invalid
    """
    try:
        token = request_obj.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return None
        
        jwt_secret = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload.get('user_id')
    except Exception:
        return None


@bp.route('', methods=['POST'])
def add_credential():
    """Add a new credential"""
    try:
        user_id = get_user_id_from_token(request)
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        website_name = data.get('website_name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        notes = data.get('notes', '').strip()
        
        if not website_name or not username or not password:
            return jsonify({'error': 'website_name, username, and password are required'}), 400
        
        # Create credential (password will be encrypted in to_dict)
        credential = Credential(
            user_id=ObjectId(user_id),
            website_name=website_name,
            username=username,
            password=password,
            notes=notes
        )
        
        result = mongo.db.credentials.insert_one(credential.to_dict(decrypt=False))
        
        return jsonify({
            'message': 'Credential added successfully',
            'credential_id': str(result.inserted_id),
            'website_name': website_name
        }), 201
    
    except Exception as e:
        return jsonify({'error': f'Failed to add credential: {str(e)}'}), 500


@bp.route('', methods=['GET'])
def get_credentials():
    """Get all credentials for the logged-in user"""
    try:
        user_id = get_user_id_from_token(request)
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        credentials = list(mongo.db.credentials.find({'user_id': ObjectId(user_id)}))
        
        # Decrypt passwords for frontend
        decrypted_credentials = []
        for cred in credentials:
            cred_obj = Credential.from_dict(cred)
            # Decrypt password
            decrypted_password = Credential.decrypt_password(cred_obj.password)
            decrypted_credentials.append({
                'id': str(cred['_id']),
                'website_name': cred['website_name'],
                'username': cred['username'],
                'password': decrypted_password,
                'notes': cred.get('notes', ''),
                'created_at': cred['created_at'].isoformat() if cred.get('created_at') else None,
                'updated_at': cred['updated_at'].isoformat() if cred.get('updated_at') else None
            })
        
        return jsonify({
            'credentials': decrypted_credentials,
            'total': len(decrypted_credentials)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve credentials: {str(e)}'}), 500


@bp.route('/<credential_id>', methods=['PUT'])
def update_credential(credential_id):
    """Update a credential"""
    try:
        user_id = get_user_id_from_token(request)
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Verify ownership
        credential = mongo.db.credentials.find_one({
            '_id': ObjectId(credential_id),
            'user_id': ObjectId(user_id)
        })
        
        if not credential:
            return jsonify({'error': 'Credential not found or unauthorized'}), 404
        
        # Update fields
        update_data = {}
        if 'website_name' in data:
            update_data['website_name'] = data['website_name'].strip()
        if 'username' in data:
            update_data['username'] = data['username'].strip()
        if 'password' in data and data['password']:
            # Encrypt new password
            update_data['password'] = Credential.encrypt_password(data['password'])
        if 'notes' in data:
            update_data['notes'] = data['notes'].strip()
        
        update_data['updated_at'] = datetime.utcnow()
        
        mongo.db.credentials.update_one(
            {'_id': ObjectId(credential_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            'message': 'Credential updated successfully',
            'credential_id': credential_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to update credential: {str(e)}'}), 500


@bp.route('/<credential_id>', methods=['DELETE'])
def delete_credential(credential_id):
    """Delete a credential"""
    try:
        user_id = get_user_id_from_token(request)
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Verify ownership before deletion
        credential = mongo.db.credentials.find_one({
            '_id': ObjectId(credential_id),
            'user_id': ObjectId(user_id)
        })
        
        if not credential:
            return jsonify({'error': 'Credential not found or unauthorized'}), 404
        
        mongo.db.credentials.delete_one({'_id': ObjectId(credential_id)})
        
        return jsonify({
            'message': 'Credential deleted successfully',
            'credential_id': credential_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to delete credential: {str(e)}'}), 500
