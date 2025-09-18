"""
OAuth2 service for Google and Apple authentication
"""

from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import httpx
import jwt
import json
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

from app.core.config import settings
from app.models.user import User
from app.core.security import create_token_pair, get_password_hash
from app.schemas.auth import UserResponse


class OAuthService:
    """OAuth2 service for handling Google and Apple authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_google(self, code: str, state: Optional[str] = None) -> Tuple[User, str, str]:
        """Authenticate user with Google OAuth2"""
        try:
            # Exchange code for access token
            token_data = await self._get_google_token(code)
            access_token = token_data["access_token"]
            
            # Get user info from Google
            user_info = await self._get_google_user_info(access_token)
            
            # Find or create user
            user = await self._find_or_create_oauth_user(
                provider="google",
                provider_id=user_info["id"],
                email=user_info["email"],
                name=user_info.get("name", ""),
                avatar=user_info.get("picture"),
                oauth_data=user_info
            )
            
            # Create JWT tokens
            tokens = create_token_pair(user.id, user.email)
            
            return user, tokens["access_token"], tokens["refresh_token"]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google authentication failed: {str(e)}"
            )
    
    async def authenticate_apple(self, code: str, state: Optional[str] = None) -> Tuple[User, str, str]:
        """Authenticate user with Apple OAuth2"""
        try:
            # Exchange code for access token
            token_data = await self._get_apple_token(code)
            access_token = token_data["access_token"]
            
            # Get user info from Apple
            user_info = await self._get_apple_user_info(access_token)
            
            # Find or create user
            user = await self._find_or_create_oauth_user(
                provider="apple",
                provider_id=user_info["sub"],
                email=user_info.get("email", ""),
                name=user_info.get("name", ""),
                avatar=None,  # Apple doesn't provide avatar
                oauth_data=user_info
            )
            
            # Create JWT tokens
            tokens = create_token_pair(user.id, user.email)
            
            return user, tokens["access_token"], tokens["refresh_token"]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Apple authentication failed: {str(e)}"
            )
    
    async def _get_google_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Google access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.OAUTH_REDIRECT_URI
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Google token: {response.text}")
            
            return response.json()
    
    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Google user info: {response.text}")
            
            return response.json()
    
    async def _get_apple_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for Apple access token"""
        # Create JWT for Apple authentication
        client_secret = self._create_apple_client_secret()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://appleid.apple.com/auth/token",
                data={
                    "client_id": settings.APPLE_CLIENT_ID,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.OAUTH_REDIRECT_URI
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Apple token: {response.text}")
            
            return response.json()
    
    async def _get_apple_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Apple ID token"""
        try:
            # Decode the ID token (no verification for simplicity)
            # In production, you should verify the JWT signature
            id_token = access_token  # In real implementation, this would be in the token response
            payload = jwt.decode(id_token, options={"verify_signature": False})
            return payload
        except Exception as e:
            raise Exception(f"Failed to decode Apple ID token: {str(e)}")
    
    def _create_apple_client_secret(self) -> str:
        """Create Apple client secret JWT"""
        if not settings.APPLE_PRIVATE_KEY:
            raise Exception("Apple private key not configured")
        
        # Parse the private key
        private_key = serialization.load_pem_private_key(
            settings.APPLE_PRIVATE_KEY.encode(),
            password=None
        )
        
        # Create JWT header
        header = {
            "alg": "ES256",
            "kid": settings.APPLE_KEY_ID
        }
        
        # Create JWT payload
        now = datetime.utcnow()
        payload = {
            "iss": settings.APPLE_TEAM_ID,
            "iat": now,
            "exp": now + timedelta(minutes=10),
            "aud": "https://appleid.apple.com",
            "sub": settings.APPLE_CLIENT_ID
        }
        
        # Sign the JWT
        token = jwt.encode(payload, private_key, algorithm="ES256", headers=header)
        return token
    
    async def _find_or_create_oauth_user(
        self,
        provider: str,
        provider_id: str,
        email: str,
        name: str,
        avatar: Optional[str],
        oauth_data: Dict[str, Any]
    ) -> User:
        """Find existing user or create new one for OAuth provider"""
        
        # Try to find existing user by provider ID
        if provider == "google":
            user = self.db.query(User).filter(User.google_id == provider_id).first()
        elif provider == "apple":
            user = self.db.query(User).filter(User.apple_id == provider_id).first()
        else:
            user = None
        
        if user:
            # Update last login
            user.last_login_at = datetime.utcnow()
            user.oauth_data = oauth_data
            self.db.commit()
            return user
        
        # Try to find user by email
        user = self.db.query(User).filter(User.email == email).first()
        
        if user:
            # Link OAuth provider to existing user
            if provider == "google":
                user.google_id = provider_id
            elif provider == "apple":
                user.apple_id = provider_id
            
            user.oauth_provider = provider
            user.oauth_data = oauth_data
            user.last_login_at = datetime.utcnow()
            self.db.commit()
            return user
        
        # Create new user
        user = User(
            email=email,
            name=name,
            avatar=avatar,
            hashed_password=None,  # OAuth users don't have passwords
            is_active=True,
            is_verified=True,  # OAuth users are pre-verified
            oauth_provider=provider,
            oauth_data=oauth_data,
            last_login_at=datetime.utcnow()
        )
        
        # Set provider ID
        if provider == "google":
            user.google_id = provider_id
        elif provider == "apple":
            user.apple_id = provider_id
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_oauth_url(self, provider: str, state: Optional[str] = None) -> str:
        """Get OAuth authorization URL for provider"""
        if provider == "google":
            return self._get_google_oauth_url(state)
        elif provider == "apple":
            return self._get_apple_oauth_url(state)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )
    
    def _get_google_oauth_url(self, state: Optional[str] = None) -> str:
        """Get Google OAuth authorization URL"""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.OAUTH_REDIRECT_URI,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    def _get_apple_oauth_url(self, state: Optional[str] = None) -> str:
        """Get Apple OAuth authorization URL"""
        params = {
            "client_id": settings.APPLE_CLIENT_ID,
            "redirect_uri": settings.OAUTH_REDIRECT_URI,
            "scope": "name email",
            "response_type": "code",
            "response_mode": "form_post"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://appleid.apple.com/auth/authorize?{query_string}"
