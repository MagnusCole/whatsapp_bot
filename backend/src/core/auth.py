from datetime import datetime, timedelta, UTC  # Add UTC here
from typing import Optional
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from .config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_api_key() -> str:
    """Create a new API key"""
    return jwt.encode(
        {"sub": "api_key", "exp": datetime.now(UTC) + timedelta(days=30)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Get and validate API key"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    try:
        payload = jwt.decode(api_key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("sub") != "api_key":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        return api_key
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify an API key"""
    if not api_key:
        return None
    try:
        payload = jwt.decode(api_key, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("sub") != "api_key":
            return None
        return api_key
    except JWTError:
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def verify_token(token: str = Security(oauth2_scheme)) -> dict:
    """Verify a JWT token"""
    if not token:
        return None
    try:
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
            
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if not payload.get("sub"):
            return None
        return payload
    except JWTError:
        return None