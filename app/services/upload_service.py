"""
Upload service
"""

import os
import uuid
from typing import List, Optional, Dict, Any, BinaryIO
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status

from app.models.upload import Upload, FileMetadata
from app.schemas.upload import UploadCreate, UploadStatus, CloudFileImport
from app.core.exceptions import NotFoundError, FileProcessingError
from app.core.config import settings
from app.services.storage_service import StorageService
from app.services.ai_service import AIService


class UploadService:
    """Upload service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.storage_service = StorageService()
        self.ai_service = AIService()
    
    def create_upload(self, user_id: str, upload_data: UploadCreate, file: UploadFile) -> Upload:
        """Create a new upload"""
        # Validate file type
        file_extension = file.filename.split('.')[-1].lower() if file.filename else ''
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise FileProcessingError(f"File type {file_extension} not allowed")
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.MAX_FILE_SIZE:
            raise FileProcessingError(f"File size exceeds maximum allowed size")
        
        # Reset file pointer
        await file.seek(0)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{file_extension}"
        
        # Upload to storage
        url = await self.storage_service.upload_file(file_content, filename)
        
        # Create upload record
        upload = Upload(
            user_id=user_id,
            subject_id=upload_data.subject_id,
            name=upload_data.name,
            type=upload_data.type.value,
            size=len(file_content),
            url=url,
            status=UploadStatus.PROCESSING.value
        )
        
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        
        # Start background processing
        await self._process_file_async(upload.id)
        
        return upload
    
    def get_uploads(self, user_id: str, subject_id: Optional[str] = None) -> List[Upload]:
        """Get all uploads for a user"""
        query = self.db.query(Upload).filter(Upload.user_id == user_id)
        
        if subject_id:
            query = query.filter(Upload.subject_id == subject_id)
        
        return query.all()
    
    def get_upload(self, upload_id: str, user_id: str) -> Optional[Upload]:
        """Get a specific upload"""
        return self.db.query(Upload).filter(
            Upload.id == upload_id,
            Upload.user_id == user_id
        ).first()
    
    def delete_upload(self, upload_id: str, user_id: str) -> bool:
        """Delete an upload"""
        upload = self.get_upload(upload_id, user_id)
        if not upload:
            return False
        
        # Delete from storage
        await self.storage_service.delete_file(upload.url)
        
        # Delete from database
        self.db.delete(upload)
        self.db.commit()
        
        return True
    
    def get_upload_status(self, upload_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get upload processing status"""
        upload = self.get_upload(upload_id, user_id)
        if not upload:
            return None
        
        return {
            "id": str(upload.id),
            "status": upload.status,
            "processing_error": upload.processing_error,
            "processed_at": upload.processed_at,
            "metadata": upload.metadata
        }
    
    async def process_upload(self, upload_id: str, user_id: str, force_reprocess: bool = False) -> bool:
        """Process an upload"""
        upload = self.get_upload(upload_id, user_id)
        if not upload:
            return False
        
        if upload.status == UploadStatus.COMPLETED.value and not force_reprocess:
            return True
        
        try:
            # Update status to processing
            upload.status = UploadStatus.PROCESSING.value
            self.db.commit()
            
            # Process the file
            await self._process_file_async(upload.id)
            
            return True
        except Exception as e:
            # Update status to failed
            upload.status = UploadStatus.FAILED.value
            upload.processing_error = str(e)
            self.db.commit()
            
            return False
    
    async def _process_file_async(self, upload_id: str) -> None:
        """Process file asynchronously"""
        upload = self.db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            return
        
        try:
            # Download file content
            file_content = await self.storage_service.download_file(upload.url)
            
            # Process based on file type
            metadata = await self._extract_metadata(file_content, upload.type)
            
            # Update upload with metadata
            upload.metadata = metadata
            upload.status = UploadStatus.COMPLETED.value
            upload.processed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            upload.status = UploadStatus.FAILED.value
            upload.processing_error = str(e)
            self.db.commit()
    
    async def _extract_metadata(self, file_content: bytes, file_type: str) -> Dict[str, Any]:
        """Extract metadata from file content"""
        metadata = {
            "keywords": [],
            "language": "it"
        }
        
        try:
            if file_type == "pdf":
                # Extract text from PDF
                text = await self.ai_service.extract_pdf_text(file_content)
                metadata["extracted_text"] = text
                metadata["pages"] = await self.ai_service.count_pdf_pages(file_content)
                
            elif file_type in ["image"]:
                # Extract text from image using OCR
                text = await self.ai_service.extract_image_text(file_content)
                metadata["extracted_text"] = text
                metadata["dimensions"] = await self.ai_service.get_image_dimensions(file_content)
                
            elif file_type == "video":
                # Extract audio and convert to text
                text = await self.ai_service.extract_video_text(file_content)
                metadata["extracted_text"] = text
                metadata["duration"] = await self.ai_service.get_video_duration(file_content)
                
            elif file_type == "text":
                # Process text content
                text = file_content.decode('utf-8')
                metadata["extracted_text"] = text
            
            # Generate summary and keywords
            if metadata.get("extracted_text"):
                summary = await self.ai_service.generate_summary(metadata["extracted_text"])
                keywords = await self.ai_service.extract_keywords(metadata["extracted_text"])
                
                metadata["summary"] = summary
                metadata["keywords"] = keywords
                metadata["language"] = await self.ai_service.detect_language(metadata["extracted_text"])
        
        except Exception as e:
            # If metadata extraction fails, still mark as completed
            pass
        
        return metadata
    
    def import_cloud_file(self, user_id: str, import_data: CloudFileImport) -> Upload:
        """Import file from cloud service"""
        # This would integrate with cloud services
        # For now, create a placeholder upload
        upload = Upload(
            user_id=user_id,
            subject_id=import_data.subject_id,
            name=import_data.name,
            type=import_data.type.value,
            size=import_data.size,
            url=f"cloud://{import_data.cloud_service.value}/{import_data.file_id}",
            cloud_service=import_data.cloud_service.value,
            cloud_file_id=import_data.file_id,
            status=UploadStatus.PROCESSING.value
        )
        
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        
        return upload
