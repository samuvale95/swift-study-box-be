"""
Custom middleware for Swift Study Box
"""

import time
import structlog
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.database import get_redis
from app.core.exceptions import RateLimitError

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response tracking"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.redis = get_redis()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if await self._is_rate_limited(client_ip):
            raise RateLimitError("Rate limit exceeded")
        
        # Process request
        response = await call_next(request)
        
        # Update rate limit counter
        await self._update_rate_limit(client_ip)
        
        return response
    
    async def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        if not self.redis:
            return False
            
        try:
            key = f"rate_limit:{client_ip}"
            current_requests = self.redis.get(key)
            
            if current_requests is None:
                return False
            
            return int(current_requests) >= settings.RATE_LIMIT_PER_MINUTE
        except Exception as e:
            # If Redis is unavailable, allow request
            logger.warning(f"Rate limiting unavailable: {e}")
            return False
    
    async def _update_rate_limit(self, client_ip: str) -> None:
        """Update rate limit counter"""
        if not self.redis:
            return
            
        try:
            key = f"rate_limit:{client_ip}"
            
            # Increment counter
            current_requests = self.redis.incr(key)
            
            # Set expiration if this is the first request
            if current_requests == 1:
                self.redis.expire(key, 60)  # 1 minute
        except Exception as e:
            # If Redis is unavailable, ignore
            logger.warning(f"Rate limiting update failed: {e}")
            pass
