"""
Progress schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ProgressBase(BaseModel):
    """Base progress schema"""
    total_sessions: int = 0
    total_time: int = 0  # in minutes
    average_score: float = 0.0
    streak: int = 0  # consecutive days
    last_study_date: Optional[datetime] = None


class ProgressResponse(ProgressBase):
    """Progress response schema"""
    id: str
    user_id: str
    subject_id: Optional[str] = None
    achievements: List[Dict[str, Any]] = []
    goals: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AchievementBase(BaseModel):
    """Base achievement schema"""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category: str  # study, quiz, exam, streak, etc.
    points: int = 0


class AchievementResponse(AchievementBase):
    """Achievement response schema"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoalBase(BaseModel):
    """Base goal schema"""
    title: str
    description: Optional[str] = None
    category: str  # study_time, quiz_score, etc.
    target_value: float
    unit: str  # minutes, percentage, count, etc.
    deadline: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Goal creation schema"""
    subject_id: Optional[str] = None


class GoalUpdate(BaseModel):
    """Goal update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    deadline: Optional[datetime] = None


class GoalResponse(GoalBase):
    """Goal response schema"""
    id: str
    user_id: str
    subject_id: Optional[str] = None
    current_value: float = 0.0
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgressStats(BaseModel):
    """Progress statistics schema"""
    overall_progress: ProgressResponse
    subject_progress: List[ProgressResponse]
    recent_achievements: List[AchievementResponse]
    active_goals: List[GoalResponse]
    completed_goals: List[GoalResponse]
    study_streak: int
    total_study_time: int
    average_daily_time: float
