"""
Quiz schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, field_validator


class QuizQuestionBase(BaseModel):
    """Base quiz question schema"""
    type: str  # single, multiple
    question: str
    options: List[str]
    correct_answer: Union[int, List[int]]
    explanation: Optional[str] = None
    difficulty: str = "medium"
    points: int = 1


class QuizQuestionCreate(QuizQuestionBase):
    """Quiz question creation schema"""
    source_upload_id: Optional[str] = None


class QuizQuestionResponse(QuizQuestionBase):
    """Quiz question response schema"""
    id: str
    quiz_id: str
    source_upload_id: Optional[str] = None
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class QuizBase(BaseModel):
    """Base quiz schema"""
    title: str
    difficulty: str = "medium"
    time_limit: Optional[int] = None
    description: Optional[str] = None
    tags: List[str] = []


class QuizCreate(QuizBase):
    """Quiz creation schema"""
    subject_id: str
    questions: Optional[List[QuizQuestionCreate]] = []


class QuizUpdate(BaseModel):
    """Quiz update schema"""
    title: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    """Quiz response schema"""
    id: str
    user_id: str
    subject_id: str
    is_active: bool
    questions: List[QuizQuestionResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class QuizStartRequest(BaseModel):
    """Quiz start request schema"""
    quiz_id: str


class QuizAnswer(BaseModel):
    """Quiz answer schema"""
    question_id: str
    answer: Union[int, List[int], str]
    time_spent: int = 0  # in seconds


class QuizSubmitRequest(BaseModel):
    """Quiz submit request schema"""
    quiz_id: str
    answers: List[QuizAnswer]


class QuizResult(BaseModel):
    """Quiz result schema"""
    quiz_id: str
    score: float
    max_score: float
    percentage: float
    correct_answers: int
    total_questions: int
    time_spent: int  # in seconds
    completed_at: datetime
    answers: List[Dict[str, Any]]


class QuizGenerationRequest(BaseModel):
    """Quiz generation request schema"""
    subject_id: str
    title: str
    difficulty: str = "medium"
    num_questions: int = 5
    time_limit: Optional[int] = None
    source_upload_ids: Optional[List[str]] = None
    tags: List[str] = []


class QuizStats(BaseModel):
    """Quiz statistics schema"""
    total_quizzes: int
    total_questions: int
    average_score: float
    total_time: int  # in minutes
    completion_rate: float
    difficulty_distribution: Dict[str, int]
