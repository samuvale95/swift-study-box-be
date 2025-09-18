"""
Grade model for academic transcript
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime, date

from app.models.base import BaseModel


class Grade(BaseModel):
    """Grade model for academic transcript"""
    
    __tablename__ = "grades"
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False)
    
    # Exam information
    exam_name = Column(String(255), nullable=False)
    grade = Column(Float, nullable=False)  # Voto ottenuto
    max_grade = Column(Float, nullable=True)  # Voto massimo (opzionale)
    credits = Column(Integer, nullable=True)  # CFU/crediti
    
    # Academic information
    exam_date = Column(Date, nullable=False)
    academic_year = Column(String(20), nullable=False)  # es. "2023-2024"
    semester = Column(String(20), nullable=True)  # es. "primo", "secondo"
    
    # Additional information
    professor = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
    
    @property
    def percentage(self) -> Optional[float]:
        """Calculate percentage if max_grade is available"""
        if self.max_grade and self.max_grade > 0:
            return (self.grade / self.max_grade) * 100
        return None
    
    @property
    def is_passed(self) -> bool:
        """Check if the grade is passing (assuming 18/30 is passing)"""
        if self.max_grade:
            return self.percentage >= 60  # 60% is passing
        return self.grade >= 18  # 18/30 is passing
