"""
Quiz management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.quiz import (
    QuizCreate, 
    QuizUpdate, 
    QuizResponse, 
    QuizStartRequest,
    QuizSubmitRequest,
    QuizResult,
    QuizGenerationRequest,
    QuizStats
)
from app.services.quiz_service import QuizService

router = APIRouter()


def get_quiz_service(db: Session = Depends(get_db)) -> QuizService:
    """Get quiz service"""
    return QuizService(db)


@router.get("/", response_model=List[QuizResponse])
async def get_quizzes(
    subject_id: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Get all quizzes for the current user"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        quizzes = quiz_service.get_quizzes(user_id, subject_id)
        return quizzes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Create a new quiz"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        quiz = quiz_service.create_quiz(user_id, quiz_data)
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Get a specific quiz"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        quiz = quiz_service.get_quiz(quiz_id, user_id)
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Update a quiz"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        quiz = quiz_service.update_quiz(quiz_id, user_id, quiz_data)
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Delete a quiz"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        success = quiz_service.delete_quiz(quiz_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        return {"message": "Quiz deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{quiz_id}/start", response_model=QuizResponse)
async def start_quiz(
    quiz_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Start a quiz session"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        quiz = quiz_service.start_quiz(quiz_id, user_id)
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(
    quiz_id: str,
    submit_data: QuizSubmitRequest,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Submit quiz answers"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        result = quiz_service.submit_quiz(quiz_id, user_id, submit_data.answers)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{quiz_id}/results", response_model=QuizResult)
async def get_quiz_results(
    quiz_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Get quiz results (placeholder)"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        # This would retrieve saved results from study sessions
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Quiz results retrieval not implemented yet"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    generation_data: QuizGenerationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Generate quiz using AI"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        quiz = await quiz_service.generate_quiz(user_id, generation_data)
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats", response_model=QuizStats)
async def get_quiz_stats(
    subject_id: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    quiz_service: QuizService = Depends(get_quiz_service)
):
    """Get quiz statistics"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        stats = quiz_service.get_quiz_stats(user_id, subject_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
