"""
Subject schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator


class SubjectBase(BaseModel):
    """Base subject schema"""
    name: str
    color: str = "#3B82F6"
    icon: str = "book"
    description: Optional[str] = None
    tags: List[str] = []


class SubjectCreate(SubjectBase):
    """Subject creation schema"""
    pass


class SubjectUpdate(BaseModel):
    """Subject update schema"""
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    
    @field_validator('color', mode='before')
    @classmethod
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            raise ValueError('Color must be a valid hex color')
        return v


class SubjectResponse(SubjectBase):
    """Subject response schema"""
    id: str
    user_id: str
    total_quizzes: int
    total_exams: int
    average_score: float
    study_time: int
    last_activity: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SubjectStats(BaseModel):
    """Subject statistics schema"""
    total_quizzes: int
    total_exams: int
    average_score: float
    study_time: int
    last_activity: Optional[datetime] = None
    total_uploads: int = 0
    total_concept_maps: int = 0
    completion_rate: float = 0.0
