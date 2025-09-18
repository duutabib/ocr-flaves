import os 
import requests
import json
import base64
from typing import Optional, Dict, Any
from processors.document_processor import EnhancedDocumentProcessor
from core.scoring import ModelScorer, ModelScore
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
    
    def _call_model_api(self, file_path: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Make API call to the model with the given file and prompt."""
        try:
            image_b64 = self.get_image_base64(file_path)
            if not image_b64:
                return None
                
            payload = {
                "images": [image_b64],
                "prompt": prompt,
                "model": self.model_name,
                "stream": False,
            }
            
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling model API: {e}")
            return None
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the raw API response into a structured format."""
        try:
            # This is a simple parser - you may need to adjust based on your model's response format
            if not response:
                return {}
                
            # Try to parse JSON if response is a string
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                    return {"raw_response": response}
            
            # If response has a 'response' field, use that
            if "response" in response:
                return response["response"]
                
            return response
            
        except Exception as e:
            print(f"Error parsing response: {e}")
            return {}
    
    def process_document(
        self, 
        file_path: str, 
        prompt_text: str = None,
        return_scored: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Process a document with the model.
        
        Args:
            file_path: Path to the document to process
            prompt_text: Optional custom prompt text
            return_scored: If True, returns a ModelScore object instead of raw response
            
        Returns:
            Dict with processed data or ModelScore if return_scored is True
        """
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}")
            return None
            
        if not self.doc_processor.is_supported_file_type(file_path):
            ext = self.doc_processor.get_file_extension(file_path)
            print(f"Error: Unsupported file type: {ext}")
            return None
            
        try:
            # Extract text first
            extracted_text = self.extract_text(file_path)
            if not extracted_text:
                return None
                
            # Detect document type
            doc_type = self.doc_processor._detect_document_type(extracted_text)
            prompt = prompt_text or self.doc_processor._get_extraction_prompt(doc_type)
            
            # Process with the model
            response = self._call_model_api(file_path, prompt)
            parsed_response = self._parse_response(response)
            
            if return_scored:
                return ModelScorer.score_response(
                    model_name=self.model_name,
                    response=parsed_response,
                    document_type=doc_type
                )
            return parsed_response
            
        except Exception as e:
            print(f"Error processing document: {e}")
            return None
        


def process_with_model(
    client: ModelClient, 
    file_path: str, 
    prompt: str = None, 
    model_name: str = None,
    enable_scoring: bool = False
):
    """
    Process a document with type detection and appropriate prompting.
    
    Args:
        client: The ModelClient instance to use
        file_path: Path to the document to process
        prompt: Optional custom prompt text
        model_name: Name of the model being used (for display purposes)
        enable_scoring: If True, uses the scoring system to evaluate the response
    """
    print(f"\n{'='*50}")
    print(f"Processing with {model_name or 'default model'}...")
    print(f"File: {file_path}")
    
    # Process the document with or without scoring
    if enable_scoring:
        result = client.process_document(file_path, prompt, return_scored=True)
        if result and isinstance(result, ModelScore):
            print("\nModel Score:")
            print("-"*50)
            print(f"Model: {result.model_name}")
            print(f"Overall Score: {result.score:.2f}/1.00")
            print(f"Confidence: {result.confidence*100:.1f}%")
            print("\nMetrics:")
            for metric, value in result.metrics.items():
                print(f"- {metric.capitalize()}: {value*100:.1f}%")
            
            print("\nExtracted Information:")
            print("-"*50)
            print(json.dumps(result.response, indent=2))
        else:
            print("No valid response could be scored.")
    else:
        # Process without scoring
        result = client.process_document(file_path, prompt)
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

def process_with_best_model(
    file_path: str,
    prompt: str = None,
    min_confidence: float = 0.5
) -> Optional[ModelScore]:
    """
    Process a document with all available models and return the best result.
    
    Args:
        file_path: Path to the document to process
        prompt: Optional custom prompt text
        min_confidence: Minimum confidence score required (0-1)
        
    Returns:
        ModelScore for the best result, or None if no valid results
    """
    # Initialize all available models
    models = {
        'llava': ModelClient(
            base_url=DEFAULT_MODELS['llava']['url'],
            model_name="llava"
        ),
        'bakllava': ModelClient(
            base_url=DEFAULT_MODELS['bakllava']['url'],
            model_name="bakllava"
        ),
        'internvl': ModelClient(
            base_url=DEFAULT_MODELS['internvl']['url'],
            model_name="internvl"
        )
    }
    
    print(f"\n{'#'*60}")
    print(f"# Processing with all available models")
    print(f"# File: {file_path}")
    print(f"# Minimum Confidence: {min_confidence*100:.0f}%")
    print(f"{'#'*60}")
    
    # Process with each model and collect scores
    all_scores = []
    for model_name, client in models.items():
        print(f"\n{'='*50}")
        print(f"Running {model_name}...")
        
        # Process with scoring enabled
        result = client.process_document(file_path, prompt, return_scored=True)
        
        if result and isinstance(result, ModelScore):
            all_scores.append(result)
            print(f"  - Score: {result.score:.2f}")
            print(f"  - Confidence: {result.confidence*100:.1f}%")
        else:
            print(f"  - Failed to get valid score")
    
    # Select the best model based on scores
    if all_scores:
        best_result = ModelScorer.select_best_model(all_scores, min_confidence)
        if best_result:
            print(f"\n{'#'*60}")
            print("# Best Result:")
            print(f"# Model: {best_result.model_name}")
            print(f"# Score: {best_result.score:.2f}")
            print(f"# Confidence: {best_result.confidence*100:.1f}%")
            print(f"{'#'*60}")
            
            print("\nExtracted Information:")
            print("-"*50)
            print(json.dumps(best_result.response, indent=2))
            
            return best_result
    
    print("\nNo model produced a valid result above the confidence threshold.")
    return None

def main():
    # Get user input
    input_path = input(f"Enter file or directory path [{DEFAULT_DATA_PATH}]: ") or DEFAULT_DATA_PATH
    custom_prompt = input("Enter custom prompt (or press Enter for auto): ") or None
    
    if not os.path.exists(input_path):
        print(f"Error: Path not found: {input_path}")
        return
    
    if os.path.isfile(input_path):
        # Process single file with model selection
        process_with_best_model(input_path, custom_prompt)
    else:
        # Process all supported files in directory
        for filename in os.listdir(input_path):
            file_path = os.path.join(input_path, filename)
            if os.path.isfile(file_path):
                # Initialize a client just for checking file type
                temp_client = ModelClient(
                    base_url=DEFAULT_MODELS['llava']['url'],
                    model_name="llava"
                )
                if temp_client.doc_processor.is_supported_file_type(file_path):
                    process_with_best_model(file_path, custom_prompt)

if __name__ == "__main__":
    main()
