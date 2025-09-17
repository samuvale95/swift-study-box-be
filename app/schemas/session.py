"""
Study session schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, field_validator


class StudySessionBase(BaseModel):
    """Base study session schema"""
    type: str  # quiz, exam, concept-map, summary
    content_id: str  # quiz_id, exam_id, or concept_map_id
    notes: Optional[str] = None
    tags: List[str] = []


class StudySessionCreate(StudySessionBase):
    """Study session creation schema"""
    subject_id: str


class StudySessionUpdate(BaseModel):
    """Study session update schema"""
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_completed: Optional[bool] = None


class StudySessionResponse(StudySessionBase):
    """Study session response schema"""
    id: str
    user_id: str
    subject_id: str
    quiz_id: Optional[str] = None
    exam_id: Optional[str] = None
    concept_map_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: int  # in minutes
    score: Optional[float] = None
    max_score: Optional[float] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class StudySessionStart(BaseModel):
    """Study session start schema"""
    type: str
    content_id: str
    subject_id: str


class StudySessionComplete(BaseModel):
    """Study session completion schema"""
    session_id: str
    score: Optional[float] = None
    max_score: Optional[float] = None
    notes: Optional[str] = None


class StudySessionStats(BaseModel):
    """Study session statistics schema"""
    total_sessions: int
    total_time: int  # in minutes
    average_score: float
    completion_rate: float
    sessions_by_type: Dict[str, int]
    recent_sessions: List[StudySessionResponse]
