import os
import re
import logging
from pathlib import Path
from staging.core.reliability import CircuitBreakerConfig, CircuitBreaker, RetryStrategy
from staging.core.monitor import OCRMetrics
from staging.core.security import DocumentValidator
from staging.core.performance import DocumentCache
from typing import BinaryIO, Optional
from typing import Any, Dict
from config import DOCUMENT_INDICATORS

from pathlib import Path


class EnhancedDocumentProcessor:
    """Main document class with all improvements"""
    
    # Supported file extensions and their MIME types
    EXTENSION_MAPPING = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp'
    }
    
    def __init__(self):
        self.metrics = OCRMetrics()
        self.validator = DocumentValidator()
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
        self.logging = logging.getLogger(__name__)
        self.cache = DocumentCache()
    
    @classmethod
    def get_file_extension(cls, file_path: str) -> str:
        """Get the lowercase file extension with dot."""
        return Path(file_path).suffix.lower()
    
    @classmethod
    def get_file_type(cls, file_path: str) -> str:
        """Get the file type based on its extension."""
        ext = cls.get_file_extension(file_path)
        return cls.EXTENSION_MAPPING.get(ext, 'unknown')
    
    @classmethod
    def is_supported_file_type(cls, file_path: str) -> bool:
        """Check if the file type is supported for processing.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if the file type is supported, False otherwise
        """
        ext = cls.get_file_extension(file_path)
        return ext in cls.EXTENSION_MAPPING

    @OCRMetrics().track_performance()
    def process(self, file_stream: BinaryIO, filename: str, **params) -> Dict[str, Any]:
        """Process document with all improvements"""
        try:
            # step 1: Validate input
            file_info = self.validator.validate_file(file_stream, filename) 

            # step 2 : check cachbe
            cached_result = self.cache.get(file_info['hash'], params)
            if cached_result:
                self.logger.info(f"Cache hit for document {filename}")
                return cached_result

            # step 3: Detect document type
            document_type = self._detect_document_type(file_stream)
            
            # step 4: Process document
            processor = self._get_processor(document_type)

            # step 5: Process with appropirate strategy 
            result = self.circuit_breaker.call(
                lambda: RetryStrategy.with_exponential_backoff(
                    lambda: processor.process(file_stream, **params)
                )
            )

            # step 6: cache result
            self.cache.set(file_info['hash'], params, result)


            # step 7: Log metrics
            self.metrics.log_processing_metrics(
                document_type=document_type,
                processing_time=processing_time,
                success=True,
                confidence=result.get('confidence', 0), 
            )

            return result
            
        except Exception as e:
            self.logging.error(f"Error processing document: {str(e)}")
            raise


    def _detect_document_type(cls, text: str, file_path: str = None) -> str:
        """Detect document type based on text content."""
        text = text.lower()
        
        # Calculate extract scores (# models results...)
        scores = {doc_type: sum(1 for p in patterns if re.search(p, text))
                 for doc_type, patterns in DOCUMENT_INDICATORS.items()}
        
        # Return best match or 'document' as default
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'document'


    def _get_processor(self, doc_type: str):
        """Get appropriate processor based on document type."""
        processors = {
            'invoice': InvoiceProcessor(),
            'receipt': ReceiptProcessor(),
            'document': EnhancedDocumentProcessorDocumentProcessor(),
        }
        return processors.get(doc_type, processors['document'])

    
    def _get_extraction_prompt(self, doc_type: str) -> str:
        """Get appropriate prompt based on document type."""
        prompts = {
            'invoice': "Extract: vendor, invoice number, date, amounts, items as JSON.",
            'receipt': "Extract: merchant, date, total, payment method, items as JSON.",
            'document': "Extract all key information from this document as JSON."
        }
        return prompts.get(doc_type, prompts['document'])
