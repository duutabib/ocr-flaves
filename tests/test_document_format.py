import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
from document_utils import (
    is_supported_document,
    validate_document,
    DocumentFormatError,
    get_file_mime_type
)

class TestDocumentFormatDetection:
    """Tests for document format detection functionality using python-magic."""

    def test_pdf_detection(self, sample_pdf_path):
        """Test that PDF files are correctly identified."""
        # Test file exists
        assert os.path.exists(sample_pdf_path)
        
        # Test MIME type detection
        mime_type = get_file_mime_type(sample_pdf_path)
        assert 'pdf' in mime_type.lower()
        
        # Test document validation
        assert is_supported_document(sample_pdf_path)
        validate_document(sample_pdf_path)  # Should not raise

    def test_image_detection(self, sample_image_path):
        """Test that image files are correctly identified."""
        # Test file exists
        assert os.path.exists(sample_image_path)
        
        # Test MIME type detection
        mime_type = get_file_mime_type(sample_image_path)
        assert any(img_type in mime_type.lower() 
                 for img_type in ['jpeg', 'jpg', 'png', 'image'])
        
        # Test document validation
        assert is_supported_document(sample_image_path)
        validate_document(sample_image_path)  # Should not raise

    def test_unsupported_format_handling(self, tmp_path):
        """Test that unsupported formats are properly handled."""
        # Create a test file with unsupported format
        test_file = tmp_path / "test.unsupported"
        test_file.write_text("dummy content")
        
        # Test that unsupported format is detected
        assert not is_supported_document(str(test_file))
        
        # Test that validation raises appropriate exception
        with pytest.raises(DocumentFormatError):
            validate_document(str(test_file))
    
    @patch('document_utils.get_file_mime_type')
    def test_corrupted_file_handling(self, mock_mime, tmp_path):
        """Test handling of corrupted or invalid files."""
        # Create a test file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b'%PDF-1.4\n%%EOF')  # Invalid PDF
        
        # Mock the mime type detection to simulate a corrupted file
        mock_mime.side_effect = IOError("Invalid file format")
        
        # Test that corrupted file is handled gracefully
        assert not is_supported_document(str(test_file))
        with pytest.raises(DocumentFormatError):
            validate_document(str(test_file))
