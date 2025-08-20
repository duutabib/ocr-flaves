import re
from typing import Dict, Optional

from pathlib import Path

class DocumentProcessor:
    """Handles document type detection and processing."""
    
    # Supported file extensions and their corresponding file types
    EXTENSION_MAPPING = {
        # Image formats
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.pdf': 'document',
        '.docx': 'document',
        '.xlsx': 'spreadsheet'
    }
    
    @classmethod
    def get_file_extension(cls, file_path: str) -> str:
        """Extract and return the file extension in lowercase."""
        return Path(file_path).suffix.lower()
    
    @classmethod
    def get_file_type(cls, file_path: str) -> str:
        """Determine the general file type based on its extension."""
        ext = cls.get_file_extension(file_path)
        return cls.EXTENSION_MAPPING.get(ext, 'unknown')
    
    @classmethod
    def is_supported_file_type(cls, file_path: str) -> bool:
        """Check if the file type is supported for processing."""
        ext = cls.get_file_extension(file_path)
        return ext in cls.EXTENSION_MAPPING
    
    @classmethod
    def detect_document_type(cls, text: str, file_path: str = None) -> str:
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
    
    @staticmethod
    def get_extraction_prompt(doc_type: str) -> str:
        """Get appropriate prompt based on document type."""
        prompts = {
            'invoice': "Extract: vendor, invoice number, date, amounts, items as JSON.",
            'receipt': "Extract: merchant, date, total, payment method, items as JSON.",
            'document': "Extract all key information from this document as JSON."
        }
        return prompts.get(doc_type, prompts['document'])
