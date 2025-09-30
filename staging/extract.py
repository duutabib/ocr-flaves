import os 
import requests
import json
import base64
import logging
import argparse
from mlx_vlm import load, generate, apply_chat_template
from mlx_vlm.utils import load_image
from typing import Optional, Dict, Any, List, Union
from staging.processors.document_processor import EnhancedDocumentProcessor
from staging.core.scoring import ModelScorer, ModelScore
from staging.config import DEFAULT_DATA_PATH, DEFAULT_MODELS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('extraction.log')
    ]
)
logger = logging.getLogger(__name__)

# Set url for model container...


class ModelClient:
    def __init__(self, base_url: str, model_name: str, verbose: bool = False):
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
        self.doc_processor = EnhancedDocumentProcessor()
        self.verbose = verbose
        if self.verbose:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"Initialized ModelClient with base_url={base_url}, model_name={model_name}")


    def load_image(self):
        """Load image from file."""
        try:
            if self.verbose:
                logger.debug(f"Loading image from {self.image_path}")
            image = load_image(self.image_path)
            if self.verbose:
                logger.debug(f"Image loaded successfully")
            return image
        except FileNotFoundError:
            error_msg = f"File not found: {self.image_path}"
            logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Error loading image {self.image_path}: {str(e)}"
            logger.error(error_msg, exc_info=self.verbose)
            return None
        

    def get_image_base64(self, image_path: str) -> Optional[str]:
        """Converts an image file to base64 encoded string."""
        try: 
            if self.verbose:
                logger.debug(f"Reading image file: {image_path}")
            with open(image_path, "rb") as image_file:
                data = image_file.read()
                if self.verbose:
                    logger.debug(f"Read {len(data)} bytes from {image_path}")
                return base64.b64encode(data).decode("utf-8")
        except FileNotFoundError:
            error_msg = f"File not found: {image_path}"
            logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Error reading image {image_path}: {str(e)}"
            logger.error(error_msg, exc_info=self.verbose)
            return None


    def extract_text(self, image_path: str) -> Optional[str]:
        """Extract text from image using the model."""
        try:
            if self.verbose:
                logger.info(f"Extracting text from {image_path} using {self.model_name}")
                
            image_b64 = self.get_image_base64(image_path)
            if not image_b64:
                logger.warning("Failed to get base64 encoded image")
                return None
                
            payload = {
                "images": [image_b64],
                "prompt": "Extract all data from this image verbatim.",
                "model": self.model_name,
                "stream": False,
            }
            
            if self.verbose:
                logger.debug(f"Sending request to {self.api_url}")
                logger.debug(f"Payload size: {len(str(payload))} bytes")
            
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            if self.verbose:
                logger.debug(f"Received response with status code {response.status_code}")
                logger.debug(f"Response headers: {response.headers}")
            
            result = response.json().get("response")
            if self.verbose and result:
                logger.debug(f"Extracted text length: {len(result)} characters")
                
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error while extracting text: {str(e)}"
            logger.error(error_msg, exc_info=self.verbose)
            return None
        except Exception as e:
            error_msg = f"Unexpected error while extracting text: {str(e)}"
            logger.error(error_msg, exc_info=self.verbose)
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
    enable_scoring: bool = False,
    verbose: bool = False
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
    logger.info(f"\n{'='*50}")
    logger.info(f"Processing with {model_name or 'default model'}")
    logger.info(f"File: {file_path}")
    if verbose:
        logger.debug(f"Enable scoring: {enable_scoring}")
        logger.debug(f"Custom prompt: {prompt}")
    
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
    min_confidence: float = 0.5,
    verbose: bool = False
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
            model_name="llava",
            verbose=verbose
        ),
        'bakllava': ModelClient(
            base_url=DEFAULT_MODELS['bakllava']['url'],
            model_name="bakllava",
            verbose=verbose
        ),
        #'internvl': ModelClient(
        #    base_url=DEFAULT_MODELS['internvl']['url'],
        #    model_name="internvl",
        #    verbose=verbose
        #)
    }
    
    logger.info(f"\n{'#'*60}")
    logger.info(f"# Processing with all available models")
    logger.info(f"# File: {file_path}")
    logger.info(f"# Minimum Confidence: {min_confidence*100:.0f}%")
    logger.info(f"{'#'*60}")
    
    if verbose:
        logger.debug(f"Using prompt: {prompt or 'Default prompt based on document type'}")
        logger.debug(f"Available models: {', '.join(models.keys())}")
    
    # Process with each model and collect scores
    all_scores = []
    for model_name, client in models.items():
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {model_name}...")
        
        try:
            # Process with scoring enabled
            result = client.process_document(file_path, prompt, return_scored=True)
            
            if result and isinstance(result, ModelScore):
                all_scores.append(result)
                logger.info(f"  - Score: {result.score:.2f}")
                logger.info(f"  - Confidence: {result.confidence*100:.1f}%")
                
                if verbose:
                    logger.debug(f"  - Model metrics: {result.metrics}")
            else:
                logger.warning(f"  - Failed to get valid score from {model_name}")
                
        except Exception as e:
            error_msg = f"Error processing with {model_name}: {str(e)}"
            logger.error(error_msg, exc_info=verbose)
    
    # Select the best model based on scores
    if all_scores:
        best_result = ModelScorer.select_best_model(all_scores, min_confidence)
        if best_result:
            logger.info(f"\n{'#'*60}")
            logger.info("# Best Result:")
            logger.info(f"# Model: {best_result.model_name}")
            logger.info(f"# Score: {best_result.score:.2f}")
            logger.info(f"# Confidence: {best_result.confidence*100:.1f}%")
            logger.info(f"{'#'*60}")
            
            if verbose:
                logger.debug(f"# All scores: {[(s.model_name, s.score) for s in all_scores]}")
            
            logger.info("\nExtracted Information:")
            logger.info("-"*50)
            logger.info(json.dumps(best_result.response, indent=2))
            
            # Log to file
            try:
                with open('extraction_results.json', 'a') as f:
                    result_data = {
                        'file': file_path,
                        'model': best_result.model_name,
                        'score': best_result.score,
                        'confidence': best_result.confidence,
                        'timestamp': str(datetime.now()),
                        'data': best_result.response
                    }
                    f.write(json.dumps(result_data) + '\n')
            except Exception as e:
                logger.warning(f"Failed to save results to file: {str(e)}")
            
            return best_result
    
    logger.warning("\nNo model produced a valid result above the confidence threshold.")
    return None

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract text from documents using AI models')
    parser.add_argument('path', nargs='?', default=DEFAULT_DATA_PATH,
                      help=f'Path to file or directory (default: {DEFAULT_DATA_PATH})')
    parser.add_argument('--prompt', type=str, default=None,
                      help='Custom prompt for extraction')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose logging')
    parser.add_argument('--min-confidence', type=float, default=0.5,
                      help='Minimum confidence threshold (0-1, default: 0.5)')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging level based on verbosity
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger.setLevel(log_level)
    
    input_path = args.path
    custom_prompt = args.prompt
    
    if not os.path.exists(input_path):
        print(f"Error: Path not found: {input_path}")
        return
    
    try:
        if os.path.isfile(input_path):
            # Process single file with model selection
            logger.info(f"Processing single file: {input_path}")
            process_with_best_model(
                input_path, 
                custom_prompt,
                min_confidence=args.min_confidence,
                verbose=args.verbose
            )
        else:
            # Process all supported files in directory
            logger.info(f"Processing directory: {input_path}")
            processed_count = 0
            
            for filename in sorted(os.listdir(input_path)):
                file_path = os.path.join(input_path, filename)
                if os.path.isfile(file_path):
                    # Initialize a client just for checking file type
                    temp_client = ModelClient(
                        base_url=DEFAULT_MODELS['llava']['url'],
                        model_name="llava",
                        verbose=args.verbose
                    )
                    if temp_client.doc_processor.is_supported_file_type(file_path):
                        logger.info(f"\nProcessing file {processed_count + 1}: {filename}")
                        process_with_best_model(
                            file_path, 
                            custom_prompt,
                            min_confidence=args.min_confidence,
                            verbose=args.verbose
                        )
                        processed_count += 1
            
            logger.info(f"\nProcessing complete. Processed {processed_count} files.")
            
    except KeyboardInterrupt:
        logger.info("\nProcessing interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=args.verbose)
        return 1
        
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code or 0)
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
        exit(1)
