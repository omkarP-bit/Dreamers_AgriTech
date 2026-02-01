"""
Authentication Service

Handles password hashing and basic auth for user authentication
"""

import base64
from typing import Tuple, Optional
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for password operations and basic auth"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def encode_basic_auth(email: str, password: str) -> str:
        """Encode email and password to base64 for basic auth"""
        credentials = f"{email}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded
    
    @staticmethod
    def decode_basic_auth(auth_header: str) -> Optional[Tuple[str, str]]:
        """Decode base64 basic auth header and return (email, password)"""
        try:
            # Remove 'Basic ' prefix if present
            if auth_header.startswith('Basic '):
                auth_header = auth_header[6:]
            
            decoded = base64.b64decode(auth_header).decode()
            email, password = decoded.split(':', 1)
            return email, password
        except Exception:
            return None
