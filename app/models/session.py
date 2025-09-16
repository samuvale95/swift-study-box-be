"""
Study session model and related schemas
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from app.models.base import BaseModel


class StudySession(BaseModel):
    """Study session model"""
    
    __tablename__ = "study_sessions"
    
    # Basic info
    type = Column(String(50), nullable=False)  # quiz, exam, concept-map, summary
    content_id = Column(UUID(as_uuid=True), nullable=False)  # quiz_id, exam_id, or concept_map_id
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=True)
    concept_map_id = Column(UUID(as_uuid=True), ForeignKey("concept_maps.id"), nullable=True)
    
    # Session data
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, default=0)  # in minutes
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    
    # Additional metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    subject = relationship("Subject", back_populates="study_sessions")
    quiz = relationship("Quiz", back_populates="study_sessions")
    exam = relationship("Exam", back_populates="study_sessions")
    concept_map = relationship("ConceptMap", back_populates="study_sessions")
    user_answers = relationship("UserAnswer", back_populates="study_session", cascade="all, delete-orphan")


class UserAnswer(BaseModel):
    """User answer model for study sessions"""
    
    __tablename__ = "study_session_answers"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), nullable=False)  # Can be quiz_question_id or exam_question_id
    
    # Answer data
    answer = Column(JSON, nullable=False)  # Index, list of indices, or text
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, default=0)  # in seconds
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    study_session = relationship("StudySession", back_populates="user_answers")
