"""
Upload schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from enum import Enum


class UploadType(str, Enum):
    """Upload type enum"""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    VIDEO = "video"
    LINK = "link"


class UploadStatus(str, Enum):
    """Upload status enum"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CloudService(str, Enum):
    """Cloud service enum"""
    GOOGLE_DRIVE = "google-drive"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"


class FileMetadata(BaseModel):
    """File metadata schema"""
    pages: Optional[int] = None
    duration: Optional[int] = None  # in seconds
    dimensions: Optional[Dict[str, int]] = None
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    keywords: List[str] = []
    language: str = "it"


class UploadBase(BaseModel):
    """Base upload schema"""
    name: str
    type: UploadType
    subject_id: str


class UploadCreate(UploadBase):
    """Upload creation schema"""
    pass


class UploadResponse(UploadBase):
    """Upload response schema"""
    id: str
    user_id: str
    size: int
    url: str
    cloud_service: Optional[CloudService] = None
    cloud_file_id: Optional[str] = None
    status: UploadStatus
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None
    file_metadata: FileMetadata
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UploadStatusResponse(BaseModel):
    """Upload status response schema"""
    id: str
    status: UploadStatus
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None
    metadata: Optional[FileMetadata] = None


class CloudFileImport(BaseModel):
    """Cloud file import schema"""
    file_id: str
    name: str
    type: UploadType
    size: int
    subject_id: str
    cloud_service: CloudService


class FileProcessingRequest(BaseModel):
    """File processing request schema"""
    upload_id: str
    force_reprocess: bool = False
