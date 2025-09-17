"""
Upload model and related schemas
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.base import BaseModel


class Upload(BaseModel):
    """Upload model"""
    
    __tablename__ = "uploads"
    
    # Basic info
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # pdf, image, text, video, link
    size = Column(Integer, nullable=False)  # in bytes
    url = Column(String(1000), nullable=False)
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    
    # Cloud service integration
    cloud_service = Column(String(50), nullable=True)  # google-drive, dropbox, onedrive
    cloud_file_id = Column(String(255), nullable=True)
    
    # Processing status
    status = Column(String(50), default="processing")  # processing, completed, failed
    processing_error = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # File metadata
    file_metadata = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="uploads")
    subject = relationship("Subject", back_populates="uploads")
    quiz_questions = relationship("QuizQuestion", back_populates="source_upload")
    exam_questions = relationship("ExamQuestion", back_populates="source_upload")
    concept_nodes = relationship("ConceptNode", back_populates="source_upload")


class FileMetadata:
    """File metadata schema"""
    
    def __init__(
        self,
        pages: Optional[int] = None,
        duration: Optional[int] = None,  # in seconds
        dimensions: Optional[Dict[str, int]] = None,
        extracted_text: Optional[str] = None,
        summary: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        language: str = "it"
    ):
        self.pages = pages
        self.duration = duration
        self.dimensions = dimensions or {}
        self.extracted_text = extracted_text
        self.summary = summary
        self.keywords = keywords or []
        self.language = language
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pages": self.pages,
            "duration": self.duration,
            "dimensions": self.dimensions,
            "extracted_text": self.extracted_text,
            "summary": self.summary,
            "keywords": self.keywords,
            "language": self.language
        }
