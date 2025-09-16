"""
Quiz model and related schemas
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from app.models.base import BaseModel


class Quiz(BaseModel):
    """Quiz model"""
    
    __tablename__ = "quizzes"
    
    # Basic info
    title = Column(String(255), nullable=False)
    difficulty = Column(String(50), default="medium")  # easy, medium, hard, expert
    time_limit = Column(Integer, nullable=True)  # in minutes
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Additional metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    subject = relationship("Subject", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="quiz")


class QuizQuestion(BaseModel):
    """Quiz question model"""
    
    __tablename__ = "quiz_questions"
    
    # Basic info
    type = Column(String(50), nullable=False)  # single, multiple
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of options
    correct_answer = Column(JSON, nullable=False)  # Index or list of indices
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), default="medium")
    points = Column(Integer, default=1)
    
    # Foreign keys
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    source_upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=True)
    
    # AI generation
    ai_generated = Column(Boolean, default=False)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    source_upload = relationship("Upload", back_populates="quiz_questions")
    user_answers = relationship("UserAnswer", back_populates="quiz_question", cascade="all, delete-orphan")


class UserAnswer(BaseModel):
    """User answer model"""
    
    __tablename__ = "user_answers"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quiz_question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id"), nullable=False)
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id"), nullable=True)
    
    # Answer data
    answer = Column(JSON, nullable=False)  # Index, list of indices, or text
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, default=0)  # in seconds
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    quiz_question = relationship("QuizQuestion", back_populates="user_answers")
    study_session = relationship("StudySession", back_populates="user_answers")
