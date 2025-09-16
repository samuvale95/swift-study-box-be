"""
Subject model and related schemas
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any

from app.models.base import BaseModel


class Subject(BaseModel):
    """Subject model"""
    
    __tablename__ = "subjects"
    
    # Basic info
    name = Column(String(255), nullable=False)
    color = Column(String(7), default="#3B82F6")  # Hex color
    icon = Column(String(50), default="book")  # Icon name
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Statistics
    total_quizzes = Column(Integer, default=0)
    total_exams = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    study_time = Column(Integer, default=0)  # in minutes
    last_activity = Column(DateTime(timezone=True), nullable=True)
    
    # Additional metadata
    description = Column(String(1000), nullable=True)
    tags = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="subjects")
    uploads = relationship("Upload", back_populates="subject", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="subject", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")
    concept_maps = relationship("ConceptMap", back_populates="subject", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="subject", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="subject", cascade="all, delete-orphan")


class SubjectStats:
    """Subject statistics schema"""
    
    def __init__(
        self,
        total_quizzes: int = 0,
        total_exams: int = 0,
        average_score: float = 0.0,
        study_time: int = 0,
        last_activity: Optional[datetime] = None
    ):
        self.total_quizzes = total_quizzes
        self.total_exams = total_exams
        self.average_score = average_score
        self.study_time = study_time
        self.last_activity = last_activity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_quizzes": self.total_quizzes,
            "total_exams": self.total_exams,
            "average_score": self.average_score,
            "study_time": self.study_time,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
