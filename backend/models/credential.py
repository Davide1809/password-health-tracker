"""
Credential model for storing website credentials
"""
from datetime import datetime
from bson.objectid import ObjectId
from cryptography.fernet import Fernet
import os


class Credential:
    """Model for storing encrypted website credentials"""
    
    def __init__(self, user_id, website_name, username, password, notes=None, created_at=None, updated_at=None, _id=None):
        """
        Initialize Credential object
        
        Args:
            user_id (str): MongoDB ObjectId of the user who owns this credential
            website_name (str): Name of the website (e.g., 'Gmail', 'GitHub')
            username (str): Username or email for the website
            password (str): Password (will be encrypted before storage)
            notes (str): Optional notes about the credential
            created_at (datetime): Credential creation timestamp
            updated_at (datetime): Last update timestamp
            _id (ObjectId): MongoDB document ID
        """
        self._id = _id or ObjectId()
        self.user_id = user_id
        self.website_name = website_name
        self.username = username
        self.password = password  # Will be encrypted before DB storage
        self.notes = notes or ''
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @staticmethod
    def get_cipher():
        """Get encryption cipher using environment key"""
        encryption_key = os.environ.get('CREDENTIAL_ENCRYPTION_KEY')
        if not encryption_key:
            # Generate a default key for development (NOT SECURE FOR PRODUCTION)
            encryption_key = Fernet.generate_key().decode()
            os.environ['CREDENTIAL_ENCRYPTION_KEY'] = encryption_key
        
        # Ensure key is bytes
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        return Fernet(encryption_key)
    
    @staticmethod
    def encrypt_password(password: str) -> str:
        """
        Encrypt password using Fernet symmetric encryption
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Encrypted password as string
        """
        cipher = Credential.get_cipher()
        encrypted = cipher.encrypt(password.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        """
        Decrypt password using Fernet symmetric encryption
        
        Args:
            encrypted_password (str): Encrypted password string
            
        Returns:
            str: Decrypted password
        """
        try:
            cipher = Credential.get_cipher()
            decrypted = cipher.decrypt(encrypted_password.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            # If decryption fails, return masked string
            return '***DECRYPTION_ERROR***'
    
    def to_dict(self, decrypt=False):
        """
        Convert credential to dictionary for database storage
        
        Args:
            decrypt (bool): If True, decrypt password in output
            
        Returns:
            dict: Credential as dictionary
        """
        password = self.password
        if decrypt and isinstance(self.password, str) and self.password.startswith('gAAAAAB'):
            # Already encrypted, decrypt it
            password = self.decrypt_password(self.password)
        elif not decrypt:
            # Encrypt password for storage
            password = self.encrypt_password(self.password)
        
        return {
            '_id': self._id,
            'user_id': self.user_id,
            'website_name': self.website_name,
            'username': self.username,
            'password': password,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Credential instance from dictionary"""
        return cls(
            user_id=data.get('user_id'),
            website_name=data.get('website_name'),
            username=data.get('username'),
            password=data.get('password'),  # Stored as encrypted
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            _id=data.get('_id')
        )
    
    def __repr__(self):
        return f"<Credential {self.website_name} for {self.username}>"
