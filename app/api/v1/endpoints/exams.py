"""
Exam management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.exam import (
    ExamCreate, 
    ExamUpdate, 
    ExamResponse, 
    ExamStartRequest,
    ExamSubmitRequest,
    ExamResult,
    ExamGenerationRequest,
    ExamStats
)
from app.services.exam_service import ExamService

router = APIRouter()


def get_exam_service(db: Session = Depends(get_db)) -> ExamService:
    """Get exam service"""
    return ExamService(db)


@router.get("/", response_model=List[ExamResponse])
async def get_exams(
    subject_id: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Get all exams for the current user"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        exams = exam_service.get_exams(user_id, subject_id)
        return exams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    exam_data: ExamCreate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Create a new exam"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        exam = exam_service.create_exam(user_id, exam_data)
        return exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Get a specific exam"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        exam = exam_service.get_exam(exam_id, user_id)
        
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        return exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: str,
    exam_data: ExamUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Update an exam"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        exam = exam_service.update_exam(exam_id, user_id, exam_data)
        return exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Delete an exam"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        success = exam_service.delete_exam(exam_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        return {"message": "Exam deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{exam_id}/start", response_model=ExamResponse)
async def start_exam(
    exam_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Start an exam session"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        exam = exam_service.start_exam(exam_id, user_id)
        return exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{exam_id}/submit", response_model=ExamResult)
async def submit_exam(
    exam_id: str,
    submit_data: ExamSubmitRequest,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Submit exam answers"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        result = exam_service.submit_exam(exam_id, user_id, submit_data.answers)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{exam_id}/results", response_model=ExamResult)
async def get_exam_results(
    exam_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Get exam results (placeholder)"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        # This would retrieve saved results from study sessions
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Exam results retrieval not implemented yet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/generate", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def generate_exam(
    generation_data: ExamGenerationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Generate exam using AI"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        exam = await exam_service.generate_exam(user_id, generation_data)
        return exam
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats", response_model=ExamStats)
async def get_exam_stats(
    subject_id: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    exam_service: ExamService = Depends(get_exam_service)
):
    """Get exam statistics"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        stats = exam_service.get_exam_stats(user_id, subject_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
