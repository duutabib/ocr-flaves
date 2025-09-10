import hashlib
import hmac
from typing import BinaryIO, List
import magic
from functools import wraps
from flask import request, abort


class DocumentValidator:
    """Security-focused document validation"""

    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/webp'
    ]

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB Might have to adjust this...

    @classmethod
    def validate_file(cls, file_stream: BinaryIO, filename: str) -> Dict[str, Any]:
        """Validate uploaded files for security"""
        # Check file size
        file_stream.seek(0, 2)
        file_size = file_stream.tell()
        file_stream.seek(0)

        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError(f"File size {file_size} exceeds maximum allowed size") 


        # Validate MIME type
        file_content = file_stream.read(2048)
        file_stream.seek(0)
        mime = magic.from_buffer(file_content, mime=True)
        

        # Check MIME type
        if mime not in cls.ALLOWED_MIME_TYPES:
            raise ValueError(f"File type {mime} is not allowed")

        # Generate file has for integrity... 
        file_hash = hashlib.sha256(file_stream.read()).hexdigest()
        file_stream.seek(0)

        return {
            "filename": filename,
            "mime_type": mime,
            "size": file_size,
            "hash": file_hash
        }

class RateLimiter:
    """Rate limiting implementation"""
    def __init__(self, max_requests: int, window_size: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}


    def check_rate_limit(self):
        """Decorator for rate limiting API endpoints"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                client_id = request.remote_addr
                current_time = time.time()

                if client_id not in self.requests:
                    self.requests[client_id] = []

                # Clean old requests
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if current_time - req_time < self.window_seconds
                ]

                if len(self.requests[client_id]) >= self.max_requests:
                    abort(429, description="Rate limit exceeded")

                self.requests[client_id].append(current_time)
                return func(*args, **kwargs)
            return wrapper
        return decorator
