import logging
import time
from functools import wraps
from typing import Dict, Any
import json



class OCRMetrics:
    """Centralized metrics collection for OCR operations"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.configure_logging()

    def configure_logging(self):
        """Configure structured logging for better observability"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def log_processing_metrics(self,
                               document_type: str,
                               processing_time: float,
                               success: bool,
                               confidence: float = None,
                               error: str = None):
        """Log structured metrics for monitoring"""
        metrics = {
            "document_type": document_type,
            "processing_time_ms": processing_time * 1000,
            "success": success,
            "confidence": confidence,
            "error": error
        }
        self.logger.info(f"OCR_METRICS: {json.dumps(metrics)}")


    def track_performance(self):
        """Decorator to track function performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    processing_time = time.time() - start_time
                    self.log_processing_metrics(
                        document_type=kwargs.get('document_type', 'unknown'),
                        processing_time=processing_time,
                        success=True,
                        confidence=kwargs.get('confidence', None),
                        error=None
                    )
                    return result
                except Exception as e:
                    self.log_processing_metrics(
                        document_type=kwargs.get('document_type', 'unknown'),
                        processing_time=processing_time,
                        success=False,
                        error=str(e)
                    )
                    raise
            return wrapper
        return decorator
