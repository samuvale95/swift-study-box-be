"""
Progress service
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.progress import Progress, Achievement, Goal
from app.schemas.progress import GoalCreate, GoalUpdate
from app.core.exceptions import NotFoundError, ValidationError


class ProgressService:
    """Progress service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_overall_progress(self, user_id: str) -> Progress:
        """Get overall progress for a user"""
        progress = self.db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.subject_id.is_(None)
        ).first()
        
        if not progress:
            # Create default progress if it doesn't exist
            progress = Progress(
                user_id=user_id,
                subject_id=None
            )
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
        
        return progress
    
    def get_subject_progress(self, user_id: str, subject_id: str) -> Progress:
        """Get progress for a specific subject"""
        progress = self.db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.subject_id == subject_id
        ).first()
        
        if not progress:
            # Create default progress if it doesn't exist
            progress = Progress(
                user_id=user_id,
                subject_id=subject_id
            )
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
        
        return progress
    
    def update_progress(self, user_id: str, subject_id: Optional[str], progress_data: Dict[str, Any]) -> Progress:
        """Update progress data"""
        if subject_id:
            progress = self.get_subject_progress(user_id, subject_id)
        else:
            progress = self.get_overall_progress(user_id)
        
        # Update fields
        for field, value in progress_data.items():
            if hasattr(progress, field):
                setattr(progress, field, value)
        
        self.db.commit()
        self.db.refresh(progress)
        
        return progress
    
    def get_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user achievements"""
        # This would typically check against user progress and unlock achievements
        # For now, return a placeholder list
        return [
            {
                "id": "1",
                "name": "First Quiz",
                "description": "Complete your first quiz",
                "icon": "quiz",
                "category": "quiz",
                "points": 10,
                "unlocked": True,
                "unlocked_at": datetime.utcnow().isoformat()
            },
            {
                "id": "2",
                "name": "Study Streak",
                "description": "Study for 7 consecutive days",
                "icon": "fire",
                "category": "streak",
                "points": 50,
                "unlocked": False,
                "unlocked_at": None
            }
        ]
    
    def get_goals(self, user_id: str, subject_id: Optional[str] = None) -> List[Goal]:
        """Get user goals"""
        query = self.db.query(Goal).filter(Goal.user_id == user_id)
        
        if subject_id:
            query = query.filter(Goal.subject_id == subject_id)
        
        return query.all()
    
    def create_goal(self, user_id: str, goal_data: GoalCreate) -> Goal:
        """Create a new goal"""
        goal = Goal(
            user_id=user_id,
            subject_id=goal_data.subject_id,
            title=goal_data.title,
            description=goal_data.description,
            category=goal_data.category,
            target_value=goal_data.target_value,
            unit=goal_data.unit,
            deadline=goal_data.deadline
        )
        
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        
        return goal
    
    def update_goal(self, goal_id: str, user_id: str, goal_data: GoalUpdate) -> Goal:
        """Update a goal"""
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).first()
        
        if not goal:
            raise NotFoundError("Goal", goal_id)
        
        # Update fields
        for field, value in goal_data.dict(exclude_unset=True).items():
            setattr(goal, field, value)
        
        self.db.commit()
        self.db.refresh(goal)
        
        return goal
    
    def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete a goal"""
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).first()
        
        if not goal:
            return False
        
        self.db.delete(goal)
        self.db.commit()
        
        return True
    
    def get_progress_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive progress statistics"""
        # Get overall progress
        overall_progress = self.get_overall_progress(user_id)
        
        # Get subject progress
        subject_progress = self.db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.subject_id.isnot(None)
        ).all()
        
        # Get achievements
        achievements = self.get_achievements(user_id)
        recent_achievements = [a for a in achievements if a.get("unlocked")][:5]
        
        # Get goals
        goals = self.get_goals(user_id)
        active_goals = [g for g in goals if not g.is_completed]
        completed_goals = [g for g in goals if g.is_completed]
        
        # Calculate study streak
        study_streak = self._calculate_study_streak(user_id)
        
        # Calculate total study time
        total_study_time = overall_progress.total_time
        
        # Calculate average daily time (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sessions = self.db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.updated_at >= thirty_days_ago
        ).all()
        
        recent_study_time = sum(p.total_time for p in recent_sessions)
        average_daily_time = recent_study_time / 30 if recent_study_time > 0 else 0
        
        return {
            "overall_progress": overall_progress,
            "subject_progress": subject_progress,
            "recent_achievements": recent_achievements,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "study_streak": study_streak,
            "total_study_time": total_study_time,
            "average_daily_time": average_daily_time
        }
    
    def _calculate_study_streak(self, user_id: str) -> int:
        """Calculate study streak in days"""
        # This would typically look at study sessions
        # For now, return a placeholder
        return 0
