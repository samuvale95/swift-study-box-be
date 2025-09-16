"""
Progress model and related schemas
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.base import BaseModel


class Progress(BaseModel):
    """Progress model"""
    
    __tablename__ = "progress"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)  # Null for overall progress
    
    # Statistics
    total_sessions = Column(Integer, default=0)
    total_time = Column(Integer, default=0)  # in minutes
    average_score = Column(Float, default=0.0)
    streak = Column(Integer, default=0)  # consecutive days
    last_study_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional metadata
    achievements = Column(JSON, default=list)
    goals = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    subject = relationship("Subject", back_populates="progress")


class Achievement(BaseModel):
    """Achievement model"""
    
    __tablename__ = "achievements"
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    category = Column(String(50), nullable=False)  # study, quiz, exam, streak, etc.
    
    # Requirements
    requirements = Column(JSON, nullable=False)  # Criteria to unlock
    points = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_progress = relationship("Progress", back_populates="achievements")


class Goal(BaseModel):
    """Goal model"""
    
    __tablename__ = "goals"
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)  # study_time, quiz_score, etc.
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    
    # Goal data
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String(50), nullable=False)  # minutes, percentage, count, etc.
    
    # Status
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    subject = relationship("Subject")
