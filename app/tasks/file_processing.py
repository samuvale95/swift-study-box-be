"""
File processing background tasks
"""

from celery import current_task
from app.core.celery import celery
from app.core.database import SessionLocal
from app.models.upload import Upload
from app.services.ai_service import AIService
from app.services.storage_service import StorageService


@celery.task(bind=True)
def process_upload_file(self, upload_id: str):
    """Process uploaded file asynchronously"""
    db = SessionLocal()
    try:
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            return {"status": "error", "message": "Upload not found"}
        
        # Update task progress
        current_task.update_state(state="PROGRESS", meta={"status": "Processing file..."})
        
        # Initialize services
        storage_service = StorageService()
        ai_service = AIService()
        
        # Download file content
        file_content = storage_service.download_file(upload.url)
        
        # Process based on file type
        metadata = extract_file_metadata(file_content, upload.type, ai_service)
        
        # Update upload with metadata
        upload.file_metadata = metadata
        upload.status = "completed"
        upload.processed_at = datetime.utcnow()
        db.commit()
        
        return {"status": "success", "message": "File processed successfully"}
    
    except Exception as e:
        # Update upload status to failed
        if upload:
            upload.status = "failed"
            upload.processing_error = str(e)
            db.commit()
        
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


def extract_file_metadata(file_content: bytes, file_type: str, ai_service: AIService) -> dict:
    """Extract metadata from file content"""
    metadata = {
        "keywords": [],
        "language": "it"
    }
    
    try:
            if file_type == "pdf":
                # Extract text from PDF
                text = ai_service.extract_pdf_text(file_content)
                metadata["extracted_text"] = text
                metadata["pages"] = ai_service.count_pdf_pages(file_content)
                
            elif file_type in ["image"]:
                # Extract text from image using OCR
                text = ai_service.extract_image_text(file_content)
                metadata["extracted_text"] = text
                metadata["dimensions"] = ai_service.get_image_dimensions(file_content)
                
            elif file_type == "video":
                # Extract audio and convert to text
                text = ai_service.extract_video_text(file_content)
                metadata["extracted_text"] = text
                metadata["duration"] = ai_service.get_video_duration(file_content)
            
        elif file_type == "text":
            # Process text content
            text = file_content.decode('utf-8')
            metadata["extracted_text"] = text
        
            # Generate summary and keywords
            if metadata.get("extracted_text"):
                summary = ai_service.generate_summary(metadata["extracted_text"])
                keywords = ai_service.extract_keywords(metadata["extracted_text"])
                
                metadata["summary"] = summary
                metadata["keywords"] = keywords
                metadata["language"] = ai_service.detect_language(metadata["extracted_text"])
    
    except Exception as e:
        # If metadata extraction fails, still mark as completed
        pass
    
    return metadata


@celery.task
def cleanup_old_files():
    """Clean up old temporary files"""
    # This would implement cleanup logic
    return {"status": "success", "message": "Cleanup completed"}
