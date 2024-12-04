# Invoice Processing Automation System

This project automates the extraction of key information from supplier invoices using a three-stage process for configuration and validation, followed by batch processing.

## Project Overview

The system is designed to process supplier invoices in PDF format, extract key information (invoice numbers, dates, amounts, etc.), and update an Excel spreadsheet with the extracted data. It uses a configurable approach that can be adapted for different supplier invoice formats.

## Process Flow

### Stage 1: Initial Testing (`test_single_supplier.py`)
- Converts supplier invoices to text
- Initial analysis of invoice layout and text content
- Helps identify key markers and patterns in the invoice format

### Stage 2: Configuration (`refine_supplier_targeting.py`)
- Configures supplier-specific invoice layout patterns
- Defines extraction patterns for:
  - Invoice numbers
  - Dates
  - Reference numbers
  - Pre-VAT totals
  - Total amounts
- Sets validation markers to ensure correct document type
- Configures exclusion markers to skip irrelevant documents

### Stage 3: Validation (`validate_configs.py`)
- Batch tests the configurations from Stage 2
- Tests against 30 random supplier invoices
- Validates extraction patterns
- Provides success rate metrics
- Allows configuration adjustments if needed

### Main Processing (`main.py`)
Once configurations are validated, the main script:
- Processes all supplier invoices
- Uses validated configurations
- Updates Excel table with parsed information
- Maintains processing statistics
- Provides detailed logging

## Project Structure

```
├── src/
│   ├── test_single_supplier.py
│   ├── refine_supplier_targeting.py
│   ├── validate_configs.py
│   └── main.py
├── supplier_configs/
│   ├── supplier_configs.py
│   └── supplier_configs.json
├── utils/
│   └── logging_utils.py
└── logs/
```

## Configuration System

The system uses a robust configuration management system that stores:
- Supplier-specific patterns
- Validation markers
- Exclusion markers
- Confidence thresholds
- Processing statistics

Each supplier configuration includes:
- Code and name
- Sheet identifier for Excel
- Validation markers
- Exclusion markers
- Extraction patterns for key fields
- Confidence thresholds
- Processing statistics

## Usage

1. Initial Testing:
   ```bash
   python src/test_single_supplier.py
   ```

2. Configure Supplier:
   ```bash
   python src/refine_supplier_targeting.py
   ```

3. Validate Configuration:
   ```bash
   python src/validate_configs.py
   ```

4. Process Invoices:
   ```bash
   python src/main.py
   ```

## Features

- Configurable pattern matching for different supplier formats
- Validation system to ensure accuracy
- Batch processing capabilities
- Progress tracking and statistics
- Detailed logging
- Excel integration for data updates
- Error handling and recovery
- Configuration management system

## Dependencies

- Python 3.x
- PyMuPDF (fitz)
- pandas
- openpyxl 