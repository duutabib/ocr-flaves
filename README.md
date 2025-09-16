# OCR-Flaves: Intelligent Document Processing

A powerful OCR (Optical Character Recognition) solution built with Python and Docker, designed to extract and process data from various document types including invoices, receipts, and forms.

## Development Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/yourusername/ocr-flaves.git
   cd ocr-flaves
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (recommended for code quality):
   ```bash
   pre-commit install
   ```

5. **Run tests**:
   ```bash
   pytest tests/
   ```

## Features

- **Multi-format Support**: Process images (JPG, PNG, WEBP) and PDFs
- **Advanced OCR**: Utilizes LLaVA and bakLLaVA models for accurate text extraction
- **Dockerized**: Easy deployment with Docker and Docker Compose
- **Document Type Detection**: Automatically identifies and processes different document types
- **Structured Output**: Returns clean, structured data from unstructured documents

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Git

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ocr-flaves.git
   cd ocr-flaves
   cd stagging 
   ```

2. Start the services:
   ```bash
   docker-compose up -d
   ```

3. The system will be available at `http://localhost:11434`

## Project Structure

```
.
├── data/                  # Sample invoice documents for testing
├── scaffold/              # Development and experimental code
├── stagging/              # Production-ready code and configurations
│   ├── Dockerfile.llava   # LLaVA model container
│   ├── Dockerfile.bakllava # bakLLaVA model container
│   ├── extract.py         # Main extraction logic
│   └── document_processor.py # Document processing utilities
├── .gitignore            # Git ignore file
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile.extract     # Main application Dockerfile
└── requirements.txt      # Python dependencies
```

## Usage

### Process a Single Document

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()
extracted_data = processor.process_document("path/to/your/document.pdf")
print(extracted_data)
```

### Using Docker

Build and run the service:

```bash
docker build -t ocr-flaves -f Dockerfile.extract .
docker run -p 5000:5000 ocr-flaves
```

### Project Plan

The [Project Plan](./plan.md) file contains the project plan.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
