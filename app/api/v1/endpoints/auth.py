"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.auth import (
    UserCreate, 
    UserLogin, 
    TokenResponse, 
    TokenRefresh,
    PasswordChange,
    UserPreferencesUpdate
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()
security = HTTPBearer()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get authentication service"""
    return AuthService(db)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        user = auth_service.register_user(user_data)
        
        # Create tokens for the new user
        tokens = auth_service.login_user(UserLogin(email=user_data.email, password=user_data.password))
        
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user"""
    try:
        tokens = auth_service.login_user(login_data)
        
        # Set HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 60  # 30 minutes
        )
        
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    try:
        tokens = auth_service.refresh_token(token_data.refresh_token)
        
        # Set new HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 60  # 30 minutes
        )
        
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout(response: Response):
    """Logout user"""
    # Clear the cookie
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user information"""
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        token = credentials.credentials
        user_id = get_current_user_id(token)
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


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user preferences"""
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        token = credentials.credentials
        user_id = get_current_user_id(token)
        user = auth_service.update_user_preferences(user_id, preferences.dict(exclude_unset=True))
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password"""
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        token = credentials.credentials
        user_id = get_current_user_id(token)
        user = auth_service.get_user_by_id(user_id)
        
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        from app.core.security import verify_password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(password_data.new_password)
        auth_service.db.commit()
        
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
