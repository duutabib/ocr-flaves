import pytest
import os
from pathlib import Path
from staging.config import DEFAULT_DATA_PATH


@pytest.fixture
def test_data_dir():
    """Fixture to get the path to the test data directory."""
    return os.path.join(DEFAULT_DATA_PATH)

@pytest.fixture
def sample_pdf_path(test_data_dir):
    """Fixture to get the path to a sample PDF file."""
    return os.path.join(test_data_dir, "invoice0.pdf")

@pytest.fixture
def sample_image_path(test_data_dir):
    """Fixture to get the path to a sample image file."""
    return os.path.join(test_data_dir, "invoice1.jpg")

