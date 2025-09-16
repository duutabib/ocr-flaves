import os 
import requests
import json
import base64
import time
from typing import Optional, Dict, Any
from processors.document_processor import EnhancedDocumentProcessor
from config import DEFAULT_DATA_PATH
from config import DEFAULT_MODELS

# Set url for model container...


class ModelClient:
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
        self.doc_processor = EnhancedDocumentProcessor()

    def get_image_base64(self, image_path: str) -> Optional[str]:
        """Converts an image file to base64 encoded string."""
        try: 
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            print(f"Error: {image_path} not found")
            return None
        except Exception as e:
            print(f"Error reading image {image_path}: {e}")
            return None


    def extract_text(self, image_path: str) -> Optional[str]:
        """Extract text from image using the model."""
        try:
            image_b64 = self.get_image_base64(image_path)
            if not image_b64:
                return None
                
            payload = {
                "images": [image_b64],
                "prompt": "Extract all data from this image verbatim.",
                "model": self.model_name,
                "stream": False,
            }
            
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response")
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return None
    
    def process_document(self, file_path: str, prompt_text: str = None) -> Dict[str, Any]:
        """Process a document with the model."""
        try:
            if not os.path.exists(file_path):
                print(f"Error: File not found: {file_path}")
                return None
                
            if not self.doc_processor.is_supported_file_type(file_path):
                ext = self.doc_processor.get_file_extension(file_path)
                print(f"Error: Unsupported file type: {ext}")
                return None
                
            file_type = self.doc_processor.get_file_type(file_path)
            if file_type not in ['image', 'document']:  # Add more types as needed
                print(f"Error: Unsupported file type for processing: {file_type}")
                return None
                
            # For now, we'll handle images as before
            # In the future, we can add specific handling for different file types
            image_b64 = self.get_image_base64(file_path)
            if not image_b64:
                return None

            payload = {
                "images": [image_b64],
                "prompt": prompt_text,
                "model": self.model_name,
                "stream": False,
            }

            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response")

        except requests.exceptions.RequestException as e:
            print(f"Error calling model API: {e}")
            return None
        except Exception as e:
            print(f"Error processing document: {e}")
            return None
        


def process_with_model(client: ModelClient, file_path: str, prompt: str = None, model_name: str = None):
    """Process a document with type detection and appropriate prompting."""
    print(f"\n{'='*50}")
    print(f"Processing with {model_name or 'default model'}...")
    print(f"File: {file_path}")
    
    # Process the document
    result = client.process_document(file_path, prompt)
    
    # Display results
    if result:
        print("\nExtracted Information:")
        print("-"*50)
        if isinstance(result, str):
            print(result)
        else:
            print(json.dumps(result, indent=2))
    else:
        print("No information could be extracted.")
    
    print(f"{'='*50}\n")
    
    try:
        # Step 1: Extract raw text first
        print("Extracting text from file...")
        extracted_text = client.extract_text(file_path)
        
        if not extracted_text:
            print("Failed to extract text from file.")
            return
            
        # Step 2: Detect document type and get appropriate prompt
        doc_type = client.doc_processor._detect_document_type(extracted_text)
        final_prompt = prompt or client.doc_processor._get_extraction_prompt(doc_type)
        
        print(f"Detected document type: {doc_type}")
        print(f"Using prompt: {final_prompt}")
        print("-"*50)
        
        # Step 3: Process with the final prompt
        result = client.process_document(file_path, final_prompt)
        
        # Step 4: Display results
        if result:
            print("\nExtracted Information:")
            print("-"*50)
            if isinstance(result, str):
                print(result)
            else:
                print(json.dumps(result, indent=2))
        else:
            print("No information could be extracted.")
            
    except Exception as e:
        print(f"Error during processing: {str(e)}")
    
    print(f"{'='*50}\n")


def process_directory(directory: str, client: ModelClient, prompt: str = None):
    """Process all supported files in a directory."""
    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}")
        return
        
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and client.doc_processor.is_supported_file_type(file_path):
            process_with_model(client, file_path, prompt)

def main():
    # Initialize clients for both models
    clients = [
        (DEFAULT_MODELS['llava']['tag'], ModelClient(base_url=DEFAULT_MODELS['llava']['url'], model_name="llava")),
        (DEFAULT_MODELS['bakllava']['tag'], ModelClient(base_url=DEFAULT_MODELS['bakllava']['url'], model_name="bakllava")),
        (DEFAULT_MODELS['internvl']['tag'], ModelClient(base_url=DEFAULT_MODELS['internvl']['url'], model_name="internvl"))
    ]
    
    # Example usage
    input_path = DEFAULT_DATA_PATH  # Can be a file or directory
    custom_prompt = None  # Set to None to use auto-generated prompt
    
    # Process with all available models
    for model_name, client in clients:
        print(f"\n{'#'*60}")
        print(f"# Processing with {model_name}")
        print(f"{'#'*60}")
        
        if os.path.isdir(input_path):
            process_directory(input_path, client, custom_prompt)
        elif os.path.isfile(input_path):
            process_with_model(client, input_path, custom_prompt, model_name)
        else:
            print(f"Error: Path not found: {input_path}")

if __name__ == "__main__":
    main()