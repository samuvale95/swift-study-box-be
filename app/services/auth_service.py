"""
Authentication service
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_token_pair,
    verify_token
)
from app.core.exceptions import AuthenticationError, ValidationError
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValidationError("User with this email already exists")
        
        # Create new user
        user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=get_password_hash(user_data.password)
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user or not user.hashed_password:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login user and return tokens"""
        user = self.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        # Create tokens
        tokens = create_token_pair(str(user.id), user.email)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=UserResponse.from_orm(user)
        )
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            payload = verify_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            email = payload.get("email")
            
            if not user_id or not email:
                raise AuthenticationError("Invalid refresh token")
            
            # Verify user exists and is active
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            # Create new tokens
            tokens = create_token_pair(str(user.id), user.email)
            
            return TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"],
                user=UserResponse.from_orm(user)
            )
        
        except Exception as e:
            raise AuthenticationError("Invalid refresh token")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> User:
        """Update user preferences"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        user.preferences.update(preferences)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        
        return True
