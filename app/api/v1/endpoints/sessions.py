"""
Study session management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.session import (
    StudySessionCreate, 
    StudySessionUpdate, 
    StudySessionResponse,
    StudySessionStart,
    StudySessionComplete,
    StudySessionStats
)
from app.services.session_service import SessionService

router = APIRouter()


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    """Get session service"""
    return SessionService(db)


@router.get("/", response_model=List[StudySessionResponse])
async def get_sessions(
    subject_id: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Get all study sessions for the current user"""
    try:
        user_id = get_current_user_id(token)
        sessions = session_service.get_sessions(user_id, subject_id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: StudySessionCreate,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Create a new study session"""
    try:
        user_id = get_current_user_id(token)
        session = session_service.create_session(user_id, session_data)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/start", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    start_data: StudySessionStart,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Start a new study session"""
    try:
        user_id = get_current_user_id(token)
        session = session_service.start_session(user_id, start_data)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{session_id}", response_model=StudySessionResponse)
async def get_session(
    session_id: str,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Get a specific study session"""
    try:
        user_id = get_current_user_id(token)
        session = session_service.get_session(session_id, user_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )
        
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{session_id}", response_model=StudySessionResponse)
async def update_session(
    session_id: str,
    session_data: StudySessionUpdate,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Update a study session"""
    try:
        user_id = get_current_user_id(token)
        session = session_service.update_session(session_id, user_id, session_data)
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{session_id}/complete", response_model=StudySessionResponse)
async def complete_session(
    session_id: str,
    complete_data: StudySessionComplete,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Complete a study session"""
    try:
        user_id = get_current_user_id(token)
        session = session_service.complete_session(
            session_id, 
            user_id, 
            complete_data.score, 
            complete_data.max_score
        )
        return session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Delete a study session"""
    try:
        user_id = get_current_user_id(token)
        success = session_service.delete_session(session_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Study session not found"
            )
        
        return {"message": "Study session deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/stats", response_model=StudySessionStats)
async def get_session_stats(
    subject_id: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    session_service: SessionService = Depends(get_session_service)
):
    """Get study session statistics"""
    try:
        user_id = get_current_user_id(token)
        stats = session_service.get_session_stats(user_id, subject_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
