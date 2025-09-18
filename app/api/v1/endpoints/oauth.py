"""
OAuth2 authentication endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.services.oauth_service import OAuthService
from app.schemas.auth import UserResponse, TokenResponse

router = APIRouter()


def get_oauth_service(db: Session = Depends(get_db)) -> OAuthService:
    """Get OAuth service"""
    return OAuthService(db)


@router.get("/login/{provider}")
async def oauth_login(
    provider: str,
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Initiate OAuth login with specified provider"""
    try:
        auth_url = oauth_service.get_oauth_url(provider, state)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/callback")
async def oauth_callback(
    provider: str = Query(..., description="OAuth provider (google, apple)"),
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from OAuth provider"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Handle OAuth callback from provider"""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    try:
        if provider == "google":
            user, access_token, refresh_token = await oauth_service.authenticate_google(code, state)
        elif provider == "apple":
            user, access_token, refresh_token = await oauth_service.authenticate_apple(code, state)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )
        
        # Create response with tokens
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
        
        # In a real application, you might want to redirect to frontend with tokens
        # For now, return JSON response
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/callback")
async def oauth_callback_post(
    provider: str = Query(..., description="OAuth provider (google, apple)"),
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from OAuth provider"),
    oauth_service: OAuthService = Depends(get_oauth_service)
):
    """Handle OAuth callback from provider (POST method for Apple)"""
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )
    
    try:
        if provider == "google":
            user, access_token, refresh_token = await oauth_service.authenticate_google(code, state)
        elif provider == "apple":
            user, access_token, refresh_token = await oauth_service.authenticate_apple(code, state)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )
        
        # Create response with tokens
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/providers")
async def get_oauth_providers():
    """Get available OAuth providers"""
    providers = []
    
    if settings.GOOGLE_CLIENT_ID:
        providers.append({
            "name": "google",
            "display_name": "Google",
            "login_url": "/api/v1/auth/oauth/login/google",
            "icon": "https://developers.google.com/identity/images/g-logo.png"
        })
    
    if settings.APPLE_CLIENT_ID:
        providers.append({
            "name": "apple",
            "display_name": "Apple",
            "login_url": "/api/v1/auth/oauth/login/apple",
            "icon": "https://developer.apple.com/assets/elements/icons/sign-in-with-apple/sign-in-with-apple-@2x.png"
        })
    
    return {"providers": providers}
