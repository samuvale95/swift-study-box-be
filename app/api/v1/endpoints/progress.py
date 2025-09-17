"""
Progress management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.progress import (
    ProgressResponse,
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    ProgressStats
)
from app.services.progress_service import ProgressService

router = APIRouter()


def get_progress_service(db: Session = Depends(get_db)) -> ProgressService:
    """Get progress service"""
    return ProgressService(db)


@router.get("/", response_model=ProgressResponse)
async def get_overall_progress(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get overall progress for the current user"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        progress = progress_service.get_overall_progress(user_id)
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/{subject_id}", response_model=ProgressResponse)
async def get_subject_progress(
    subject_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get progress for a specific subject"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        progress = progress_service.get_subject_progress(user_id, subject_id)
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/stats", response_model=ProgressStats)
async def get_progress_stats(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get comprehensive progress statistics"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        stats = progress_service.get_progress_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/achievements", response_model=List[dict])
async def get_achievements(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get user achievements"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        achievements = progress_service.get_achievements(user_id)
        return achievements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(
    subject_id: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Get user goals"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        goals = progress_service.get_goals(user_id, subject_id)
        return goals
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Create a new goal"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        goal = progress_service.create_goal(user_id, goal_data)
        return goal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Update a goal"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        goal = progress_service.update_goal(goal_id, user_id, goal_data)
        return goal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    progress_service: ProgressService = Depends(get_progress_service)
):
    """Delete a goal"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        success = progress_service.delete_goal(goal_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return {"message": "Goal deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
