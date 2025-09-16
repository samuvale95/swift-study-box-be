"""
Upload management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, get_current_user_id
from app.schemas.upload import (
    UploadResponse, 
    UploadStatusResponse, 
    CloudFileImport,
    FileProcessingRequest
)
from app.services.upload_service import UploadService

router = APIRouter()


def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    """Get upload service"""
    return UploadService(db)


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    type: str = Form(...),
    subject_id: str = Form(...),
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Upload a new file"""
    try:
        user_id = get_current_user_id(token)
        
        # Create upload data
        from app.schemas.upload import UploadCreate, UploadType
        upload_data = UploadCreate(
            name=name,
            type=UploadType(type),
            subject_id=subject_id
        )
        
        upload = await upload_service.create_upload(user_id, upload_data, file)
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[UploadResponse])
async def get_uploads(
    subject_id: Optional[str] = None,
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Get all uploads for the current user"""
    try:
        user_id = get_current_user_id(token)
        uploads = upload_service.get_uploads(user_id, subject_id)
        return uploads
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: str,
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Get a specific upload"""
    try:
        user_id = get_current_user_id(token)
        upload = upload_service.get_upload(upload_id, user_id)
        
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: str,
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Delete an upload"""
    try:
        user_id = get_current_user_id(token)
        success = await upload_service.delete_upload(upload_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        return {"message": "Upload deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{upload_id}/process")
async def process_upload(
    upload_id: str,
    request: FileProcessingRequest,
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Process an upload"""
    try:
        user_id = get_current_user_id(token)
        success = await upload_service.process_upload(
            upload_id, 
            user_id, 
            request.force_reprocess
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        return {"message": "Upload processing started"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{upload_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: str,
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Get upload processing status"""
    try:
        user_id = get_current_user_id(token)
        status_info = upload_service.get_upload_status(upload_id, user_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found"
            )
        
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/cloud/connect")
async def connect_cloud_service(
    service: str,
    token: str = Depends(oauth2_scheme)
):
    """Connect to cloud service (placeholder)"""
    # This would implement OAuth flow for cloud services
    return {"message": f"Connecting to {service} service"}


@router.post("/cloud/disconnect")
async def disconnect_cloud_service(
    service: str,
    token: str = Depends(oauth2_scheme)
):
    """Disconnect from cloud service (placeholder)"""
    return {"message": f"Disconnected from {service} service"}


@router.get("/cloud/files")
async def get_cloud_files(
    service: str,
    token: str = Depends(oauth2_scheme)
):
    """Get files from cloud service (placeholder)"""
    return {"files": [], "service": service}


@router.post("/cloud/import", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def import_cloud_file(
    import_data: CloudFileImport,
    token: str = Depends(oauth2_scheme),
    upload_service: UploadService = Depends(get_upload_service)
):
    """Import file from cloud service"""
    try:
        user_id = get_current_user_id(token)
        upload = upload_service.import_cloud_file(user_id, import_data)
        return upload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
