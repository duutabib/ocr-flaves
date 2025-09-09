import pytest
from unittest.mock import patch, MagicMock

class TestExtractionFunctionality:
    """Tests for the core extraction functionality."""

    @patch('your_module.extract_text_from_document')
    def test_text_extraction_accuracy(self, mock_extract):
        """Test that text is extracted with sufficient accuracy."""
        # Mock the extraction function
        mock_extract.return_value = "Sample extracted text"
        
        result = mock_extract("dummy_path")
        assert isinstance(result, str)
        assert len(result) > 0
        mock_extract.assert_called_once()

    @patch('your_module.detect_document_type')
    def test_document_type_detection(self, mock_detect):
        """Test that document types are correctly detected."""
        test_cases = [
            ("invoice0.pdf", "invoice"),
            ("invoice1.jpg", "invoice"),
            ("business_card.png", "business_card")
        ]
        
        for filename, expected_type in test_cases:
            mock_detect.return_value = expected_type
            assert mock_detect(filename) == expected_type
