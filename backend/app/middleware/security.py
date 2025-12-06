"""
Security middleware for production deployment.
Includes rate limiting, security headers, and input sanitization.
"""
import time
import logging
from typing import Callable, Dict
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse.
    Implements a sliding window algorithm for rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store request timestamps per IP
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque())
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        current_time = time.time()
        
        # Clean old entries (older than 1 hour)
        history = self.request_history[client_ip]
        while history and current_time - history[0] > 3600:
            history.popleft()
        
        # Check rate limits
        minute_ago = current_time - 60
        
        recent_requests = sum(1 for t in history if t > minute_ago)
        hourly_requests = len(history)
        
        if recent_requests >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded (per minute) for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )
        
        if hourly_requests >= self.requests_per_hour:
            logger.warning(f"Rate limit exceeded (per hour) for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Hourly rate limit exceeded. Please try again later."}
            )
        
        # Add current request
        history.append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.requests_per_minute - recent_requests - 1)
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.requests_per_hour - hourly_requests - 1)
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses for enhanced security.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' http://localhost:* ws://localhost:*;"
        )
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS Protection
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
        
        return response


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import os
    import re
    
    # Get basename to prevent path traversal
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except dots, dashes, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Ensure filename doesn't start with a dot
    if filename.startswith('.'):
        filename = '_' + filename[1:]
    
    # Limit filename length
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    filename = name + ext
    
    return filename


def validate_file_content(file_path: str, allowed_types: list) -> bool:
    """
    Validate file content using magic numbers (file signatures).
    
    Args:
        file_path: Path to file
        allowed_types: List of allowed file extensions
        
    Returns:
        True if file is valid, False otherwise
    """
    import os
    
    # Check file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in allowed_types:
        return False
    
    # Check file size (max 100MB)
    max_size = 100 * 1024 * 1024
    if os.path.getsize(file_path) > max_size:
        return False
    
    # Check magic numbers for common file types
    magic_numbers = {
        '.csv': [b''],  # CSV doesn't have a magic number
        '.xlsx': [b'PK\x03\x04'],  # ZIP-based formats
        '.xls': [b'\xD0\xCF\x11\xE0'],  # OLE2 format
    }
    
    if file_ext in magic_numbers:
        with open(file_path, 'rb') as f:
            header = f.read(8)
            expected_headers = magic_numbers[file_ext]
            
            # CSV is special case (no magic number)
            if file_ext == '.csv':
                return True
            
            # Check if header matches any expected magic number
            if not any(header.startswith(magic) for magic in expected_headers):
                return False
    
    return True
