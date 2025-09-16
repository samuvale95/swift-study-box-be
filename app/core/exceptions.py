"""
Custom exceptions for Swift Study Box
"""

from typing import Optional, Dict, Any


class SwiftStudyBoxException(Exception):
    """Base exception for Swift Study Box"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(SwiftStudyBoxException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(SwiftStudyBoxException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class ValidationError(SwiftStudyBoxException):
    """Validation related errors"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(SwiftStudyBoxException):
    """Resource not found errors"""
    
    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )


class ConflictError(SwiftStudyBoxException):
    """Resource conflict errors"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR"
        )


class RateLimitError(SwiftStudyBoxException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class FileProcessingError(SwiftStudyBoxException):
    """File processing errors"""
    
    def __init__(self, message: str = "File processing failed"):
        super().__init__(
            message=message,
            status_code=422,
            error_code="FILE_PROCESSING_ERROR"
        )


class AIProcessingError(SwiftStudyBoxException):
    """AI processing errors"""
    
    def __init__(self, message: str = "AI processing failed"):
        super().__init__(
            message=message,
            status_code=422,
            error_code="AI_PROCESSING_ERROR"
        )


class CloudServiceError(SwiftStudyBoxException):
    """Cloud service errors"""
    
    def __init__(self, service: str, message: str = "Cloud service error"):
        super().__init__(
            message=f"{service}: {message}",
            status_code=502,
            error_code="CLOUD_SERVICE_ERROR"
        )
