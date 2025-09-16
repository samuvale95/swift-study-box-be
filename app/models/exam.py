"""
Exam model and related schemas
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from app.models.base import BaseModel


class Exam(BaseModel):
    """Exam model"""
    
    __tablename__ = "exams"
    
    # Basic info
    title = Column(String(255), nullable=False)
    difficulty = Column(String(50), default="medium")  # easy, medium, hard, expert
    time_limit = Column(Integer, nullable=False)  # in minutes
    total_points = Column(Integer, default=0)
    passing_score = Column(Integer, default=60)  # percentage
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Additional metadata
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="exams")
    subject = relationship("Subject", back_populates="exams")
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="exam")


class ExamQuestion(BaseModel):
    """Exam question model"""
    
    __tablename__ = "exam_questions"
    
    # Basic info
    type = Column(String(50), nullable=False)  # single, multiple, open
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # List of options (null for open questions)
    correct_answer = Column(JSON, nullable=True)  # Index, list of indices, or text
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), default="medium")
    points = Column(Integer, default=1)
    
    # Foreign keys
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    source_upload_id = Column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=True)
    
    # AI generation
    ai_generated = Column(Boolean, default=False)
    
    # Relationships
    exam = relationship("Exam", back_populates="questions")
    source_upload = relationship("Upload", back_populates="exam_questions")
    user_answers = relationship("UserAnswer", back_populates="exam_question", cascade="all, delete-orphan")


class UserAnswer(BaseModel):
    """User answer model for exams"""
    
    __tablename__ = "exam_user_answers"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exam_question_id = Column(UUID(as_uuid=True), ForeignKey("exam_questions.id"), nullable=False)
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id"), nullable=True)
    
    # Answer data
    answer = Column(JSON, nullable=False)  # Index, list of indices, or text
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Integer, default=0)  # in seconds
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    exam_question = relationship("ExamQuestion", back_populates="user_answers")
    study_session = relationship("StudySession", back_populates="user_answers")
