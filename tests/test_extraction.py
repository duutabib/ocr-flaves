#!/usr/bin/env python3
"""
Simple test script for OCR extraction without interactive input
"""

import os
import sys
sys.path.append('.')

from staging.extract import ModelClient, process_with_model

def test_extraction():
    # Test file path
    test_file = "/Users/duuta/ocr-flaves/data/invoice1.jpg"

    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return

    print(f"Testing OCR extraction on: {test_file}")

    # Initialize the model client
    client = ModelClient(
        base_url="http://localhost:11434",
        model_name="llava"
    )

    # Test the extraction
    try:
        result = process_with_model(
            client=client,
            file_path=test_file,
            prompt=None,
            model_name="llava",
            enable_scoring=False
        )
        print("Extraction completed successfully!")

    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    test_extraction()