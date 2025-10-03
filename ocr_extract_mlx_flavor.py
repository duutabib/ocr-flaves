#!/usr/bin/env python3
"""
Working OCR extractor for invoice data with proper timeout handling
"""
import argparse
import requests
import json
import base64
import os
import sys
import time
import logging
import mlx.core as mx
from mlx_vlm.utils import load_image
from mlx_vlm import generate, load


# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('working_ocr_extractor.log')
    ]
)
logger = logging.getLogger(__name__)


def extract_invoice_data_mlx(image_path, model=None,  model_proc=None, timeout=180):
    """
    Extract invoice data with proper timeout and error handling
    """
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None

    print(f"📄 Processing invoice: {os.path.basename(image_path)}")
    logger.info(f"⏰ Timeout set to {timeout} seconds (be patient, this can take 2-3 minutes)")

    try:
        # Load the image directly using load_image with the path
        image = load_image(image_path)
        logger.info("✅ Image loaded successfully")

        # Set default chat template if not set
        if not hasattr(model_proc.tokenizer, 'chat_template') or not model_proc.tokenizer.chat_template:
            model_proc.tokenizer.chat_template = """
            {% if messages[0]['role'] == 'system' %}
                {% set system_message = messages[0]['content'] %}
                {% set messages = messages[1:] %}
            {% else %}
                {% set system_message = 'You are a helpful assistant that extracts information from invoices.' %}
            {% endif %}
            
            {{ bos_token }}
            {% for message in messages %}
                {% if message['role'] == 'user' %}
                    {{ '<|user|>\n' + message['content'] }}
                {% elif message['role'] == 'assistant' %}
                    {{ '<|assistant|>\n' + message['content'] + eos_token }}
                {% endif %}
                {% if not loop.last %}{{ '\n' }}{% endif %}
            {% endfor %}
            <|assistant|>
            """

        # Prepare the chat template
        messages = [
            {"role": "user", "content": "<image>\nExtract the key information from this invoice: vendor name, invoice number, date, total amount, and main items. Present it in a clear, structured format."}
        ]
        prompt = model_proc.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        # Prepare extraction request
        payload = {
            "model": model,
            "processor": model_proc,
            "prompt": prompt,
            "images": [image],
            "verbose": False,
        }

        logger.info("🚀 Starting extraction...")
        start_time = time.time()

        # Call generate with the payload
        response = generate(
            model=model,
            processor=model_proc,
            prompt=prompt,
            images=[image],
            verbose=False,
        )

        end_time = time.time()
        duration = end_time - start_time

        if not response:
            logger.error(f"❌ Extraction failed: {response}")
            return None

        #result = response.json()
        #extracted_text = result.get('response', 'No response')

        logger.info(f"✅ SUCCESS! Extraction completed in {duration:.1f} seconds")
        print("=" * 70)
        print(f"EXTRACTED INVOICE DATA:")
        print("=" * 70)
        logger.info(f"Here is the response: {response}")
        print("=" * 70)

        # Save results
        output_file = f"{os.path.splitext(image_path)[0]}_extracted.txt"
        with open(output_file, 'w') as f:
            f.write(f"Invoice: {image_path}\n")
            f.write(f"Extraction Time: {duration:.1f} seconds\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n")
            f.write(extracted_text)

        print(f"💾 Results saved to: {output_file}")
        return extracted_text

    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Request timed out after {timeout} seconds")
        logger.error("💡 Try increasing timeout or check system resources")
        return None
    except Exception as e:
        logger.error(f"❌ Error during extraction: {e}")
        return None


def process_directory(directory_path, timeout=180):
    """Process all supported images in a directory"""
    supported_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.pdf']

    if not os.path.isdir(directory_path):
        print(f"❌ Directory not found: {directory_path}")
        return

    files = []
    for filename in os.listdir(directory_path):
        if any(filename.lower().endswith(ext) for ext in supported_extensions):
            files.append(os.path.join(directory_path, filename))

    if not files:
        logger.error(f"❌ No supported files found in {directory_path}")
        return

    logger.info(f"📁 Found {len(files)} files to process")

    results = []
    for i, file_path in enumerate(files, 1):
        logger.info(f"\n[{i}/{len(files)}] " + "="*50)
        result = extract_invoice_data_mlx(file_path, timeout)
        results.append((file_path, result))

        if result:
            logger.info(f"✅ File {i} completed successfully")
        else:
            logger.error(f"❌ File {i} failed")

    # Summary
    successful = sum(1 for _, result in results if result)
    logger.info(f"\n📊 PROCESSING COMPLETE")
    logger.info(f"✅ Successful: {successful}/{len(files)} files")
    logger.info(f"❌ Failed: {len(files) - successful}/{len(files)} files")


def create_parser():
    parser = argparse.ArgumentParser(description="Extract invoice data with proper timeout and error handling")
    parser.add_argument(
            "--image_path_or_dir", 
            type=str, 
            default=os.path.join(os.getcwd(), "/data/invoices1.jpg"),
            required=True,
            help="Path to image or directory containing images"
        )
    parser.add_argument(
            "--timeout", 
            type=int, 
            default=180,
            help="Timeout in seconds"
        )
    return parser


def main():
        
    parser = create_parser()
    args = parser.parse_args()
    input_path = args.image_path_or_dir
    timeout = args.timeout

    # load model
    model, model_proc = load("mlx-community/llava-1.5-7b-4bit")

    logger.info(f"🚀 OCR Invoice Data Extractor")
    print("=" * 60)

    if os.path.isfile(input_path):
        # Process single file
        extract_invoice_data_mlx(input_path, model, model_proc, timeout)
    elif os.path.isdir(input_path):
        # Process directory
        process_directory(input_path, model, model_proc, timeout)
    else:
        logger.error(f"❌ Path not found: {input_path}")


if __name__ == "__main__":
    main()