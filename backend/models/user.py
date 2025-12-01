"""
User model for MongoDB
"""
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt


class User:
    """User model representing a registered user in the system"""
    
    def __init__(self, email, password_hash, name=None, created_at=None, updated_at=None, _id=None, 
                 security_question_id=None, security_answer_hash=None):
        """
        Initialize User object
        
        Args:
            email (str): User's email address
            password_hash (str): Hashed password
            name (str): User's full name
            created_at (datetime): Account creation timestamp
            updated_at (datetime): Last update timestamp
            _id (ObjectId): MongoDB document ID
            security_question_id (int): ID of chosen security question
            security_answer_hash (str): Hashed security question answer
        """
        self._id = _id or ObjectId()
        self.email = email
        self.password_hash = password_hash
        self.name = name or 'User'
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.security_question_id = security_question_id
        self.security_answer_hash = security_answer_hash
    
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
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'security_question_id': self.security_question_id,
            'security_answer_hash': self.security_answer_hash
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create User instance from dictionary"""
        return cls(
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            name=data.get('name'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            _id=data.get('_id'),
            security_question_id=data.get('security_question_id'),
            security_answer_hash=data.get('security_answer_hash')
        )
    
    def __repr__(self):
        return f"<User {self.email}>"
