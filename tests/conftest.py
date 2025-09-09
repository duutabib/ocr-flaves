import pytest
import os
from pathlib import Path
from config import DEFAULT_DATA_PATH

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
test_data_dir = DEFAULT_DATA_PATH

@pytest.fixture
def test_data_dir():
    """Fixture to get the path to the test data directory."""
    return os.path.join(PROJECT_ROOT, "tests", "test_data")

@pytest.fixture
def sample_pdf_path(test_data_dir):
    """Fixture to get the path to a sample PDF file."""
    return os.path.join(test_data_dir,"invoice.pdf")

@pytest.fixture
def sample_image_path(test_data_dir):
    """Fixture to get the path to a sample image file."""
    return os.path.join(test_data_dir, "invoice1.jpg")

# Add more fixtures as needed
