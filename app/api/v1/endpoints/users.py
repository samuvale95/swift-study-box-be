"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.auth import UserResponse, UserPreferencesUpdate
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get authentication service"""
    return AuthService(db)


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user profile"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user profile"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user fields
        for field, value in user_data.items():
            if hasattr(user, field) and field not in ['id', 'created_at', 'updated_at']:
                setattr(user, field, value)
        
        auth_service.db.commit()
        auth_service.db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/preferences")
async def get_preferences(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user preferences"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user.preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user preferences"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        user = auth_service.update_user_preferences(user_id, preferences.dict(exclude_unset=True))
        
        return user.preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/account")
async def delete_account(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Delete user account"""
    try:
        if not credentials:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        

        user_id = get_current_user_id(credentials.credentials)
        success = auth_service.deactivate_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Account deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
