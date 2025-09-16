"""
Subject service
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectStats
from app.core.exceptions import NotFoundError, ValidationError


class SubjectService:
    """Subject service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_subject(self, user_id: str, subject_data: SubjectCreate) -> Subject:
        """Create a new subject"""
        subject = Subject(
            user_id=user_id,
            name=subject_data.name,
            color=subject_data.color,
            icon=subject_data.icon,
            description=subject_data.description,
            tags=subject_data.tags
        )
        
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        
        return subject
    
    def get_subjects(self, user_id: str) -> List[Subject]:
        """Get all subjects for a user"""
        return self.db.query(Subject).filter(Subject.user_id == user_id).all()
    
    def get_subject(self, subject_id: str, user_id: str) -> Optional[Subject]:
        """Get a specific subject"""
        return self.db.query(Subject).filter(
            Subject.id == subject_id,
            Subject.user_id == user_id
        ).first()
    
    def update_subject(self, subject_id: str, user_id: str, subject_data: SubjectUpdate) -> Subject:
        """Update a subject"""
        subject = self.get_subject(subject_id, user_id)
        if not subject:
            raise NotFoundError("Subject", subject_id)
        
        # Update fields
        for field, value in subject_data.dict(exclude_unset=True).items():
            setattr(subject, field, value)
        
        self.db.commit()
        self.db.refresh(subject)
        
        return subject
    
    def delete_subject(self, subject_id: str, user_id: str) -> bool:
        """Delete a subject"""
        subject = self.get_subject(subject_id, user_id)
        if not subject:
            return False
        
        self.db.delete(subject)
        self.db.commit()
        
        return True
    
    def get_subject_stats(self, subject_id: str, user_id: str) -> SubjectStats:
        """Get subject statistics"""
        subject = self.get_subject(subject_id, user_id)
        if not subject:
            raise NotFoundError("Subject", subject_id)
        
        # Calculate additional stats
        total_uploads = len(subject.uploads) if subject.uploads else 0
        total_concept_maps = len(subject.concept_maps) if subject.concept_maps else 0
        
        # Calculate completion rate (simplified)
        total_sessions = subject.total_quizzes + subject.total_exams
        completed_sessions = sum(1 for session in subject.study_sessions if session.is_completed) if subject.study_sessions else 0
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0.0
        
        return SubjectStats(
            total_quizzes=subject.total_quizzes,
            total_exams=subject.total_exams,
            average_score=subject.average_score,
            study_time=subject.study_time,
            last_activity=subject.last_activity,
            total_uploads=total_uploads,
            total_concept_maps=total_concept_maps,
            completion_rate=completion_rate
        )
    
    def update_subject_stats(self, subject_id: str, user_id: str, stats_data: Dict[str, Any]) -> Subject:
        """Update subject statistics"""
        subject = self.get_subject(subject_id, user_id)
        if not subject:
            raise NotFoundError("Subject", subject_id)
        
        # Update stats
        for field, value in stats_data.items():
            if hasattr(subject, field):
                setattr(subject, field, value)
        
        self.db.commit()
        self.db.refresh(subject)
        
        return subject
