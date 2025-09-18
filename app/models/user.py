"""
User model and related schemas
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from app.models.base import BaseModel


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    # Basic info
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    avatar = Column(String(500), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    preferences = Column(JSON, default={
        "language": "it",
        "difficulty": "medium",
        "study_mode": "mixed",
        "notifications": True
    })
    
    # Subscription
    subscription_type = Column(String(50), default="free")  # free, premium, pro
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # OAuth providers
    google_id = Column(String(255), nullable=True, unique=True)
    apple_id = Column(String(255), nullable=True, unique=True)
    microsoft_id = Column(String(255), nullable=True, unique=True)
    
    # OAuth provider info
    oauth_provider = Column(String(50), nullable=True)  # google, apple, microsoft
    oauth_data = Column(JSON, nullable=True)  # Store additional OAuth data
    
    # Relationships
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    uploads = relationship("Upload", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    concept_maps = relationship("ConceptMap", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    grades = relationship("Grade", back_populates="user", cascade="all, delete-orphan")


class UserPreferences:
    """User preferences schema"""
    
    def __init__(
        self,
        language: str = "it",
        difficulty: str = "medium",
        study_mode: str = "mixed",
        notifications: bool = True
    ):
        self.language = language
        self.difficulty = difficulty
        self.study_mode = study_mode
        self.notifications = notifications
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "difficulty": self.difficulty,
            "study_mode": self.study_mode,
            "notifications": self.notifications
        }
