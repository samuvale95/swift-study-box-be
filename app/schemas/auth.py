"""
Authentication schemas
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """User creation schema"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema"""
    id: str
    avatar: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    preferences: Dict[str, Any]
    subscription_type: str
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserPreferencesUpdate(BaseModel):
    """User preferences update schema"""
    language: Optional[str] = None
    difficulty: Optional[str] = None
    study_mode: Optional[str] = None
    notifications: Optional[bool] = None
    
    @validator('language')
    def validate_language(cls, v):
        if v and v not in ['it', 'en']:
            raise ValueError('Language must be either "it" or "en"')
        return v
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v and v not in ['easy', 'medium', 'hard', 'expert']:
            raise ValueError('Difficulty must be one of: easy, medium, hard, expert')
        return v
    
    @validator('study_mode')
    def validate_study_mode(cls, v):
        if v and v not in ['visual', 'textual', 'mixed']:
            raise ValueError('Study mode must be one of: visual, textual, mixed')
        return v
