"""
User model for MongoDB
"""
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt


class User:
    """User model representing a registered user in the system"""
    
    def __init__(self, email, password_hash, created_at=None, updated_at=None, _id=None):
        """
        Initialize User object
        
        Args:
            email (str): User's email address
            password_hash (str): Hashed password
            created_at (datetime): Account creation timestamp
            updated_at (datetime): Last update timestamp
            _id (ObjectId): MongoDB document ID
        """
        self._id = _id or ObjectId()
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password (str): Plain text password to verify
            password_hash (str): Stored password hash
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user to dictionary for database storage"""
        return {
            '_id': self._id,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create User instance from dictionary"""
        return cls(
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            _id=data.get('_id')
        )
    
    def __repr__(self):
        return f"<User {self.email}>"
