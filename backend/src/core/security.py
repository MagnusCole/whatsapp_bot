import secrets
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select

def create_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def verify_api_key(api_key: str, db: Session) -> Optional[str]:
    """Verify if the API key is valid and return the associated user_id"""
    # In a real application, you would verify against a database
    # For testing purposes, we'll accept any non-empty key
    if api_key and len(api_key) > 0:
        return "test_user"
    return None

def get_api_key_from_header(authorization: str) -> Optional[str]:
    """Extract API key from the Authorization header"""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None