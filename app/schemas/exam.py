"""
Exam schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, validator


class ExamQuestionBase(BaseModel):
    """Base exam question schema"""
    type: str  # single, multiple, open
    question: str
    options: Optional[List[str]] = None
    correct_answer: Optional[Union[int, List[int], str]] = None
    explanation: Optional[str] = None
    difficulty: str = "medium"
    points: int = 1


class ExamQuestionCreate(ExamQuestionBase):
    """Exam question creation schema"""
    source_upload_id: Optional[str] = None


class ExamQuestionResponse(ExamQuestionBase):
    """Exam question response schema"""
    id: str
    exam_id: str
    source_upload_id: Optional[str] = None
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExamBase(BaseModel):
    """Base exam schema"""
    title: str
    difficulty: str = "medium"
    time_limit: int  # in minutes
    total_points: int = 0
    passing_score: int = 60  # percentage
    description: Optional[str] = None
    instructions: Optional[str] = None
    tags: List[str] = []


class ExamCreate(ExamBase):
    """Exam creation schema"""
    subject_id: str
    questions: Optional[List[ExamQuestionCreate]] = []


class ExamUpdate(BaseModel):
    """Exam update schema"""
    title: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: Optional[int] = None
    total_points: Optional[int] = None
    passing_score: Optional[int] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ExamResponse(ExamBase):
    """Exam response schema"""
    id: str
    user_id: str
    subject_id: str
    is_active: bool
    questions: List[ExamQuestionResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ExamStartRequest(BaseModel):
    """Exam start request schema"""
    exam_id: str


class ExamAnswer(BaseModel):
    """Exam answer schema"""
    question_id: str
    answer: Union[int, List[int], str]
    time_spent: int = 0  # in seconds


class ExamSubmitRequest(BaseModel):
    """Exam submit request schema"""
    exam_id: str
    answers: List[ExamAnswer]


class ExamResult(BaseModel):
    """Exam result schema"""
    exam_id: str
    score: float
    max_score: float
    percentage: float
    passed: bool
    correct_answers: int
    total_questions: int
    time_spent: int  # in seconds
    completed_at: datetime
    answers: List[Dict[str, Any]]


class ExamGenerationRequest(BaseModel):
    """Exam generation request schema"""
    subject_id: str
    title: str
    difficulty: str = "medium"
    num_questions: int = 10
    time_limit: int = 60  # in minutes
    passing_score: int = 60
    source_upload_ids: Optional[List[str]] = None
    tags: List[str] = []


class ExamStats(BaseModel):
    """Exam statistics schema"""
    total_exams: int
    total_questions: int
    average_score: float
    pass_rate: float
    total_time: int  # in minutes
    completion_rate: float
    difficulty_distribution: Dict[str, int]
