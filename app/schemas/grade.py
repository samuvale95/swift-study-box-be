"""
Grade schemas for academic transcript
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator


class GradeBase(BaseModel):
    """Base grade schema"""
    exam_name: str
    grade: float
    max_grade: Optional[float] = None
    credits: Optional[int] = None
    exam_date: date
    academic_year: str
    semester: Optional[str] = None
    professor: Optional[str] = None
    notes: Optional[str] = None


class GradeCreate(GradeBase):
    """Grade creation schema"""
    subject_id: str


class GradeUpdate(BaseModel):
    """Grade update schema"""
    exam_name: Optional[str] = None
    grade: Optional[float] = None
    max_grade: Optional[float] = None
    credits: Optional[int] = None
    exam_date: Optional[date] = None
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    professor: Optional[str] = None
    notes: Optional[str] = None


class GradeResponse(GradeBase):
    """Grade response schema"""
    id: str
    user_id: str
    subject_id: str
    subject_name: Optional[str] = None
    percentage: Optional[float] = None
    is_passed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class GradeStats(BaseModel):
    """Grade statistics schema"""
    total_credits: int
    earned_credits: int
    average_grade: float
    weighted_average: float
    total_exams: int
    passed_exams: int
    failed_exams: int
    current_gpa: float
    academic_progress: float
    by_semester: Dict[str, Dict[str, Any]]
    by_subject: Dict[str, Dict[str, Any]]


class GradeSummary(BaseModel):
    """Grade summary for dashboard"""
    subject_name: str
    subject_id: str
    total_exams: int
    average_grade: float
    last_grade: Optional[float] = None
    last_exam_date: Optional[date] = None
    credits: int
    is_passed: bool


class AcademicYearStats(BaseModel):
    """Academic year statistics"""
    academic_year: str
    total_exams: int
    average_grade: float
    credits: int
    semester_breakdown: Dict[str, Dict[str, Any]]
