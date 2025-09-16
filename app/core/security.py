"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from app.core.config import settings
from app.core.exceptions import AuthenticationError

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            raise AuthenticationError("Invalid token type")
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            raise AuthenticationError("Token expired")
        
        return payload
    
    except JWTError:
        raise AuthenticationError("Invalid token")


def get_current_user_id(token: str) -> str:
    """Get current user ID from token"""
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise AuthenticationError("Invalid token payload")
    
    return user_id


class OAuth2PasswordBearerWithCookie(HTTPBearer):
    """OAuth2 password bearer that also checks cookies"""
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        # Check Authorization header first
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        
        if authorization and scheme.lower() == "bearer":
            return HTTPAuthorizationCredentials(scheme=scheme, credentials=param)
        
        # Check cookies
        token = request.cookies.get("access_token")
        if token:
            return HTTPAuthorizationCredentials(scheme="bearer", credentials=token)
        
        return None


# Create OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearerWithCookie()


def get_token_from_request(request: Request) -> Optional[str]:
    """Extract token from request"""
    # Check Authorization header
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    
    # Check cookies
    return request.cookies.get("access_token")


def create_token_pair(user_id: str, email: str) -> dict[str, str]:
    """Create access and refresh token pair"""
    access_token = create_access_token({"sub": user_id, "email": email})
    refresh_token = create_refresh_token({"sub": user_id, "email": email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
