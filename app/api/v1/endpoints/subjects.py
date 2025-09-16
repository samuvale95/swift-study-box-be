"""
Subject management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse, SubjectStats
from app.services.subject_service import SubjectService

router = APIRouter()


def get_subject_service(db: Session = Depends(get_db)) -> SubjectService:
    """Get subject service"""
    return SubjectService(db)


@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    token: str = Depends(oauth2_scheme),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """Get all subjects for the current user"""
    try:
        user_id = get_current_user_id(token)
        subjects = subject_service.get_subjects(user_id)
        return subjects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    token: str = Depends(oauth2_scheme),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """Create a new subject"""
    try:
        user_id = get_current_user_id(token)
        subject = subject_service.create_subject(user_id, subject_data)
        return subject
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: str,
    token: str = Depends(oauth2_scheme),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """Get a specific subject"""
    try:
        user_id = get_current_user_id(token)
        subject = subject_service.get_subject(subject_id, user_id)
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        return subject
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    subject_data: SubjectUpdate,
    token: str = Depends(oauth2_scheme),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """Update a subject"""
    try:
        user_id = get_current_user_id(token)
        subject = subject_service.update_subject(subject_id, user_id, subject_data)
        return subject
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    token: str = Depends(oauth2_scheme),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """Delete a subject"""
    try:
        user_id = get_current_user_id(token)
        success = subject_service.delete_subject(subject_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        return {"message": "Subject deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{subject_id}/stats", response_model=SubjectStats)
async def get_subject_stats(
    subject_id: str,
    token: str = Depends(oauth2_scheme),
    subject_service: SubjectService = Depends(get_subject_service)
):
    """Get subject statistics"""
    try:
        user_id = get_current_user_id(token)
        stats = subject_service.get_subject_stats(subject_id, user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
