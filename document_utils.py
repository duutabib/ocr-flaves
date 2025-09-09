"""
Utility functions for document format detection using python-magic.
"""
import os
import magic
from typing import Optional, List, Set
from pathlib import Path

# Supported MIME types for documents
SUPPORTED_MIME_TYPES = {
    # PDF documents
    'application/pdf',
    
    # Images
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/bmp',
    'image/webp',
    
    # Office documents
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.oasis.opendocument.text',
}

# File extensions for supported formats
SUPPORTED_EXTENSIONS = {
    # Documents
    '.pdf',
    
    # Images
    '.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp',
    
    # Office
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt',
}

class DocumentFormatError(ValueError):
    """Raised when a document format is not supported or invalid."""
    pass

def get_file_mime_type(file_path: str) -> str:
    """
    Get the MIME type of a file using python-magic.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: MIME type of the file
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there's an error reading the file
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path).lower()
    except Exception as e:
        raise IOError(f"Error detecting file type: {str(e)}")

def is_supported_document(file_path: str) -> bool:
    """
    Check if a file is a supported document format.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if the file is a supported document format, False otherwise
    """
    try:
        # First check by extension for quick filtering
        ext = os.path.splitext(file_path)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            return True
            
        # Then verify with magic for more accurate detection
        mime_type = get_file_mime_type(file_path)
        return any(supported in mime_type for supported in SUPPORTED_MIME_TYPES)
    except (FileNotFoundError, IOError):
        return False

def validate_document(file_path: str) -> None:
    """
    Validate that a file is a supported document format.
    
    Args:
        file_path: Path to the file to validate
        
    Raises:
        DocumentFormatError: If the file is not a supported document format
        FileNotFoundError: If the file does not exist
        IOError: If there's an error reading the file
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    mime_type = get_file_mime_type(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext not in SUPPORTED_EXTENSIONS and \
       not any(supported in mime_type for supported in SUPPORTED_MIME_TYPES):
        raise DocumentFormatError(
            f"Unsupported file format: {mime_type} (extension: {ext or 'none'})")

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python document_utils.py <file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        validate_document(file_path)
        mime_type = get_file_mime_type(file_path)
        print(f"File is valid. MIME type: {mime_type}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
