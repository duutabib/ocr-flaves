# Containerization and Integration Plan for extract.py

## Notes
- Fixed indentation and parameter bugs in extract.py
- Improved extract.py to interact with both LLaVA and bakLLaVA containers
- Confirmed best practice: containerizing extract code for consistency and deployment
- Decision: Add extract.py as a service to Docker Compose
- Created requirements.txt and Dockerfile.extract for extract service
- .dockerignore created to keep container lean
- User requested document format detection to be added to extract.py

## TODO

## Task List
- [x] Add containerization for two models placeholder models.
- [x] Add containarized service for extract.py
- [x] Fix extract.py bugs and improve output formatting
- [x] Create requirements.txt for extract service
- [x] Create Dockerfile.extract for extract service
- [x] Create .dockerignore for extract context
- [x] Update docker-compose.yml to add extract-service
- [x] Implemented document type detection with `python-magic`.
- [x] Add internVL model service to system
- [x] System works end to end reliably.
- [x] Test extract-service container with llava and bakllava services
- [x] Move document indicators to config file
- [x] Implement document format detection in extract.py
- [x] Implement scoring for the models based on response quality... 
- [x] Implement MLX-vlm processor for document processing 
- [x] Move project management to uv
    - [x] move project to uv 
    - [ ] fix issues with uv move
- [x] Change in memory output to model to dict from json, but final output should be json.
- [x] Optimized system for small model and implemented testing...


### Next set of tasks...
- [ ] Implement duplicate detection for documents.
- [ ] Implement persistence of data captured as a json document with corresponding metadata, including document type, document hash, source, create date, upload date, and model used.
- [] Implement user selection for where results from models are quite different according to some tolerance.
- [] Implement data parser to standardize the output from models for consistent output by doucment type.
- [] Implement OPen AI service model

## Not urgent...
- [] Improve latency.. current testing at 2 - 3mins # not urgent

## Testing
### Unit Tests for Extraction Features

#### Test Cases for Document Format Detection
- [x] Test detection of image formats (PNG, JPG, TIFF)
- [x] Test handling of unsupported formats
- [x] Test corrupted file handling


#### Test Cases for Document Type Detection
- [ ] Test receipt detection
- [ ] Test invoice detection
- [ ] Test business card detection
- [ ] Test handwritten note detection
- [ ] Test unknown document type handling

#### Test Cases for Data Extraction
- [ ] Test text extraction accuracy
- [ ] Test table extraction
- [ ] Test data validation
- [ ] Test handling of poor quality scans
- [ ] Test extraction from different document layouts

#### Integration Tests
- [x] Test end-to-end extraction pipeline
- [ ] Test model response consistency
- [ ] Test error handling and logging
- [ ] Test performance with large documents

# Long term considerations
 --  [] Train a model from stratch.

### Test Automation
- [x] Set up pytest framework
- [ ] Create test fixtures for sample documents
- [ ] Implement CI/CD pipeline for tests
- [ ] Add code coverage reporting

## Current Goal
Test extract container with services


# current sprint 
- [] adjust based on user inputs, update model weights
- [] implement model selection based on scoring
- [] Train some small models for task
- [] Finish testing of scoring, set up models tests in regression style