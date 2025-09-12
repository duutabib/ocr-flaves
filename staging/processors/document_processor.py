import re
import logging

from staging.core.reliablity import CircuitBreakerConfig
from ..core.monitor import OCRMetrics
from ..core.security import DocumentValidator
from ..core.reliability import CircuitBreaker, RetryStrategy
from ..core.performance import AsyncDocumentProcessor, DocumentCache
from typing import Dict, Optional

from pathlib import Path


class EnhanchedDocumentProcessor:
    """Main document class with all improvements"""
    
    def __init__(self):
        self.metrics = OCRMetrics()
        self.validator = DocumentValidator()
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
        self.logging = logging.getLogger(__name__)
        self.cache = DocumentCache()

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
        
        # Document type indicators
        indicators = {
            'invoice': [
                r'invoice', 
                r'bill to', 
                r'invoice number', 
                r'date',
                r'customer',
                r'items',
                r'total', 
                r'subtotal', 
                r'tax',
            ],
            'receipt': [
                r'receipt', 
                r'payment', 
                r'tendered', 
                r'change', 
                r'cash', 
                r'card'
            ],
            'form': [
                r'form', 
                r'application', 
                r'request', 
                r'proposal', 
                r'offer', 
                r'quote'
            ],

            'purchase order': [
                r'purchase order', 
                r'po', 
                r'purchase order number', 
                r'date',
                r'customer',
                r'items',
                r'total', 
                r'subtotal', 
                r'tax',
            ],
            'bill of materials': [
                r'bill of materials', 
                r'bill of materials number', 
                r'date',
                r'customer',
                r'items',
                r'total', 
                r'subtotal', 
                r'tax',
            ],

            'deposit slip': [
                r'deposit slip', 
                r'deposit slip number', 
                r'date',
                r'customer',
                r'items',
                r'total', 
                r'subtotal', 
                r'tax',
            ],

            'credit/debit memo': [
                r'credit/debit memo', 
                r'credit/debit memo number', 
                r'date',
                r'customer',
                r'items',
                r'total', 
                r'subtotal', 
                r'tax',
            ],

            'petty cash voucher': [
                r'petty cash voucher', 
                r'petty cash voucher number', 
                r'date',
                r'customer',
                r'items',
                r'total', 
                r'subtotal', 
                r'tax',
            ],

        }
        
        # Calculate scores
        scores = {doc_type: sum(1 for p in patterns if re.search(p, text))
                 for doc_type, patterns in indicators.items()}
        
        # Return best match or 'document' as default
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'document'


    def _get_processor(self, doc_type: str):
        """Get appropriate processor based on document type."""
        processors = {
            'invoice': InvoiceProcessor(),
            'receipt': ReceiptProcessor(),
            'document': DocumentProcessor(),
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
