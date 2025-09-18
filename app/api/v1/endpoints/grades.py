"""
Grade management endpoints for academic transcript
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.grade import (
    GradeCreate, 
    GradeUpdate, 
    GradeResponse, 
    GradeStats,
    GradeSummary,
    AcademicYearStats
)
from app.services.grade_service import GradeService

router = APIRouter()


def get_grade_service(db: Session = Depends(get_db)) -> GradeService:
    """Get grade service"""
    return GradeService(db)


@router.get("/", response_model=List[GradeResponse])
async def get_grades(
    subject_id: Optional[str] = Query(None, description="Filter by subject ID"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    semester: Optional[str] = Query(None, description="Filter by semester"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Get all grades for the current user with optional filters"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        grades = grade_service.get_grades(user_id, subject_id, academic_year, semester)
        
        # Convert to response format with subject name
        response_grades = []
        for grade in grades:
            grade_dict = {
                "id": grade.id,
                "user_id": grade.user_id,
                "subject_id": grade.subject_id,
                "subject_name": grade.subject.name if grade.subject else None,
                "exam_name": grade.exam_name,
                "grade": grade.grade,
                "max_grade": grade.max_grade,
                "credits": grade.credits,
                "exam_date": grade.exam_date,
                "academic_year": grade.academic_year,
                "semester": grade.semester,
                "professor": grade.professor,
                "notes": grade.notes,
                "percentage": grade.percentage,
                "is_passed": grade.is_passed,
                "created_at": grade.created_at,
                "updated_at": grade.updated_at
            }
            response_grades.append(GradeResponse(**grade_dict))
        
        return response_grades
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    grade_data: GradeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Add a new grade to the transcript"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        grade = grade_service.create_grade(user_id, grade_data)
        
        # Convert to response format
        grade_dict = {
            "id": grade.id,
            "user_id": grade.user_id,
            "subject_id": grade.subject_id,
            "subject_name": grade.subject.name if grade.subject else None,
            "exam_name": grade.exam_name,
            "grade": grade.grade,
            "max_grade": grade.max_grade,
            "credits": grade.credits,
            "exam_date": grade.exam_date,
            "academic_year": grade.academic_year,
            "semester": grade.semester,
            "professor": grade.professor,
            "notes": grade.notes,
            "percentage": grade.percentage,
            "is_passed": grade.is_passed,
            "created_at": grade.created_at,
            "updated_at": grade.updated_at
        }
        
        return GradeResponse(**grade_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Get a specific grade"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        grade = grade_service.get_grade(grade_id, user_id)
        
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )
        
        # Convert to response format
        grade_dict = {
            "id": grade.id,
            "user_id": grade.user_id,
            "subject_id": grade.subject_id,
            "subject_name": grade.subject.name if grade.subject else None,
            "exam_name": grade.exam_name,
            "grade": grade.grade,
            "max_grade": grade.max_grade,
            "credits": grade.credits,
            "exam_date": grade.exam_date,
            "academic_year": grade.academic_year,
            "semester": grade.semester,
            "professor": grade.professor,
            "notes": grade.notes,
            "percentage": grade.percentage,
            "is_passed": grade.is_passed,
            "created_at": grade.created_at,
            "updated_at": grade.updated_at
        }
        
        return GradeResponse(**grade_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: str,
    grade_data: GradeUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Update a grade"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        grade = grade_service.update_grade(grade_id, user_id, grade_data)
        
        # Convert to response format
        grade_dict = {
            "id": grade.id,
            "user_id": grade.user_id,
            "subject_id": grade.subject_id,
            "subject_name": grade.subject.name if grade.subject else None,
            "exam_name": grade.exam_name,
            "grade": grade.grade,
            "max_grade": grade.max_grade,
            "credits": grade.credits,
            "exam_date": grade.exam_date,
            "academic_year": grade.academic_year,
            "semester": grade.semester,
            "professor": grade.professor,
            "notes": grade.notes,
            "percentage": grade.percentage,
            "is_passed": grade.is_passed,
            "created_at": grade.created_at,
            "updated_at": grade.updated_at
        }
        
        return GradeResponse(**grade_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{grade_id}")
async def delete_grade(
    grade_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Delete a grade"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        success = grade_service.delete_grade(grade_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )
        
        return {"message": "Grade deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats/overview", response_model=GradeStats)
async def get_grade_stats(
    subject_id: Optional[str] = Query(None, description="Filter by subject ID"),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Get comprehensive grade statistics"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        stats = grade_service.get_grade_stats(user_id, subject_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/summary/dashboard", response_model=List[GradeSummary])
async def get_grade_summary(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    grade_service: GradeService = Depends(get_grade_service)
):
    """Get grade summary by subject for dashboard"""
    try:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
        user_id = get_current_user_id(credentials.credentials)
        summary = grade_service.get_grade_summary(user_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
