"""
Storage service for file management
"""

import boto3
from typing import Optional
from fastapi import HTTPException, status
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.exceptions import CloudServiceError


class StorageService:
    """Storage service for file management"""
    
    def __init__(self):
        self.s3_client = None
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
    
    async def upload_file(self, file_content: bytes, filename: str) -> str:
        """Upload file to storage"""
        if not self.s3_client or not settings.S3_BUCKET_NAME:
            # Fallback to local storage for development
            return await self._upload_local(file_content, filename)
        
        try:
            key = f"uploads/{filename}"
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=file_content,
                ContentType=self._get_content_type(filename)
            )
            return f"s3://{settings.S3_BUCKET_NAME}/{key}"
        except ClientError as e:
            raise CloudServiceError("S3", str(e))
    
    async def download_file(self, url: str) -> bytes:
        """Download file from storage"""
        if url.startswith("s3://"):
            return await self._download_s3(url)
        else:
            return await self._download_local(url)
    
    async def delete_file(self, url: str) -> bool:
        """Delete file from storage"""
        if url.startswith("s3://"):
            return await self._delete_s3(url)
        else:
            return await self._delete_local(url)
    
    async def _upload_local(self, file_content: bytes, filename: str) -> str:
        """Upload file to local storage"""
        import os
        os.makedirs("uploads", exist_ok=True)
        
        file_path = f"uploads/{filename}"
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
    
    async def _download_local(self, file_path: str) -> bytes:
        """Download file from local storage"""
        with open(file_path, "rb") as f:
            return f.read()
    
    async def _delete_local(self, file_path: str) -> bool:
        """Delete file from local storage"""
        import os
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False
    
    async def _download_s3(self, url: str) -> bytes:
        """Download file from S3"""
        if not self.s3_client:
            raise CloudServiceError("S3", "S3 client not configured")
        
        try:
            # Parse S3 URL
            bucket, key = url.replace("s3://", "").split("/", 1)
            
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise CloudServiceError("S3", str(e))
    
    async def _delete_s3(self, url: str) -> bool:
        """Delete file from S3"""
        if not self.s3_client:
            raise CloudServiceError("S3", "S3 client not configured")
        
        try:
            # Parse S3 URL
            bucket, key = url.replace("s3://", "").split("/", 1)
            
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            raise CloudServiceError("S3", str(e))
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on filename"""
        extension = filename.split('.')[-1].lower()
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        return content_types.get(extension, 'application/octet-stream')
