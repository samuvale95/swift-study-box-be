"""
Study session service
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.session import StudySession
from app.schemas.session import StudySessionCreate, StudySessionUpdate, StudySessionStart
from app.core.exceptions import NotFoundError, ValidationError


class SessionService:
    """Study session service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: str, session_data: StudySessionCreate) -> StudySession:
        """Create a new study session"""
        session = StudySession(
            user_id=user_id,
            subject_id=session_data.subject_id,
            type=session_data.type,
            content_id=session_data.content_id,
            notes=session_data.notes,
            tags=session_data.tags
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def start_session(self, user_id: str, start_data: StudySessionStart) -> StudySession:
        """Start a new study session"""
        session = StudySession(
            user_id=user_id,
            subject_id=start_data.subject_id,
            type=start_data.type,
            content_id=start_data.content_id,
            started_at=datetime.utcnow()
        )
        
        # Set the appropriate foreign key based on type
        if start_data.type == "quiz":
            session.quiz_id = start_data.content_id
        elif start_data.type == "exam":
            session.exam_id = start_data.content_id
        elif start_data.type == "concept-map":
            session.concept_map_id = start_data.content_id
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_sessions(self, user_id: str, subject_id: Optional[str] = None) -> List[StudySession]:
        """Get all study sessions for a user"""
        query = self.db.query(StudySession).filter(StudySession.user_id == user_id)
        
        if subject_id:
            query = query.filter(StudySession.subject_id == subject_id)
        
        return query.order_by(desc(StudySession.started_at)).all()
    
    def get_session(self, session_id: str, user_id: str) -> Optional[StudySession]:
        """Get a specific study session"""
        return self.db.query(StudySession).filter(
            StudySession.id == session_id,
            StudySession.user_id == user_id
        ).first()
    
    def update_session(self, session_id: str, user_id: str, session_data: StudySessionUpdate) -> StudySession:
        """Update a study session"""
        session = self.get_session(session_id, user_id)
        if not session:
            raise NotFoundError("Study session", session_id)
        
        # Update fields
        for field, value in session_data.dict(exclude_unset=True).items():
            setattr(session, field, value)
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def complete_session(self, session_id: str, user_id: str, score: Optional[float] = None, max_score: Optional[float] = None) -> StudySession:
        """Complete a study session"""
        session = self.get_session(session_id, user_id)
        if not session:
            raise NotFoundError("Study session", session_id)
        
        session.is_completed = True
        session.completed_at = datetime.utcnow()
        session.score = score
        session.max_score = max_score
        
        # Calculate duration
        if session.started_at:
            duration = session.completed_at - session.started_at
            session.duration = int(duration.total_seconds() / 60)  # Convert to minutes
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a study session"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        
        return True
    
    def get_session_stats(self, user_id: str, subject_id: Optional[str] = None) -> Dict[str, Any]:
        """Get study session statistics"""
        query = self.db.query(StudySession).filter(StudySession.user_id == user_id)
        
        if subject_id:
            query = query.filter(StudySession.subject_id == subject_id)
        
        sessions = query.all()
        
        total_sessions = len(sessions)
        total_time = sum(session.duration for session in sessions if session.duration)
        
        # Calculate average score
        completed_sessions = [s for s in sessions if s.is_completed and s.score is not None]
        average_score = 0
        if completed_sessions:
            total_score = sum(s.score for s in completed_sessions)
            average_score = total_score / len(completed_sessions)
        
        # Calculate completion rate
        completion_rate = (len(completed_sessions) / total_sessions * 100) if total_sessions > 0 else 0
        
        # Group by type
        sessions_by_type = {}
        for session in sessions:
            sessions_by_type[session.type] = sessions_by_type.get(session.type, 0) + 1
        
        # Get recent sessions (last 10)
        recent_sessions = sessions[:10]
        
        return {
            "total_sessions": total_sessions,
            "total_time": total_time,
            "average_score": average_score,
            "completion_rate": completion_rate,
            "sessions_by_type": sessions_by_type,
            "recent_sessions": recent_sessions
        }
    
    def get_study_streak(self, user_id: str) -> int:
        """Calculate study streak in days"""
        # Get all completed sessions
        sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user_id,
            StudySession.is_completed == True
        ).order_by(desc(StudySession.completed_at)).all()
        
        if not sessions:
            return 0
        
        # Calculate streak
        streak = 0
        current_date = datetime.utcnow().date()
        
        for session in sessions:
            session_date = session.completed_at.date()
            days_diff = (current_date - session_date).days
            
            if days_diff == streak:
                streak += 1
                current_date = session_date
            elif days_diff > streak + 1:
                break
        
        return streak
