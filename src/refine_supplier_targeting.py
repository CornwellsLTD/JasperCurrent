from dataclasses import dataclass
import re
import fitz
from pathlib import Path
from typing import Optional, Dict
import pandas as pd

@dataclass
class ValleyNorthernInvoiceData:
    invoice_number: str
    invoice_date: str
    due_date: str
    sub_total: float
    vat_amount: float
    total_amount: float
    confidence_score: float

def analyze_extraction_confidence(text: str, patterns: Dict[str, str]) -> dict:
    """Analyze how well patterns match the text"""
    confidence_report = {}
    for field, pattern in patterns.items():
        matches = re.finditer(pattern, text)
        matches_list = list(matches)
        confidence_report[field] = {
            'success': len(matches_list) > 0,
            'matches_found': len(matches_list),
            'sample_matches': [m.group(1) for m in matches_list[:3]]
        }
    return confidence_report

def suggest_config_settings(text: str, filename: str) -> dict:
    """Suggest configuration settings based on text analysis"""
    # Define patterns based on observed invoice structure
    patterns = {
        'invoice_number': r'(?:Invoice No[.: ]*|^)(\d{6})',  # Matches both in header and from filename
        'invoice_date': r'(?:Invoice Date[.: ]*|Date[.: ]*)(\d{2}/\d{2}/\d{4})',
        'due_date': r'(?:Inv Due By|Due Date)[.: ]*(\d{2}/\d{2}/\d{4})',
        'sub_total': r'Sub[- ]?Total\s*(\d+\.\d{2})',
        'vat_amount': r'VAT @ 20%\s*(\d+\.\d{2})',
        'total_amount': r'TOTAL DUE \(£\)\s*(\d+\.\d{2})'
    }
    
    # Extract invoice number from filename if present
    filename_match = re.search(r'^(\d{6})', filename)
    if filename_match:
        print(f"Found invoice number in filename: {filename_match.group(1)}")
    
    # Test patterns
    confidence_report = analyze_extraction_confidence(text, patterns)
    
    # Add filename-based invoice number to confidence report
    if filename_match:
        confidence_report['invoice_number'] = {
            'success': True,
            'matches_found': 1,
            'sample_matches': [filename_match.group(1)]
        }
    
    # Detect validation markers
    validation_markers = [
        "INVOICE",
        "TOTAL DUE",
        "VAT @"
    ]
    
    # Build suggested config
    suggested_config = {
        'code': 'VALLEY_NORTHERN',
        'name': 'Valley Northern Ltd',
        'sheet_identifier': 'valley northern',
        'validation_markers': validation_markers,
        'exclusion_markers': ['STATEMENT', 'Credit Note'],
        'patterns': patterns,
        'high_confidence_threshold': 95.0,
        'review_confidence_threshold': 75.0
    }
    
    # Print confidence report
    print("\n=== Pattern Matching Confidence Report ===")
    for field, result in confidence_report.items():
        print(f"\n{field}:")
        print(f"Success: {result['success']}")
        print(f"Matches found: {result['matches_found']}")
        if result['sample_matches']:
            print(f"Sample matches: {result['sample_matches']}")
    
    return suggested_config, confidence_report

def extract_valley_northern_data(pdf_path: str) -> Optional[ValleyNorthernInvoiceData]:
    """Extract data from Valley Northern invoice"""
    try:
        # Extract text from PDF
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        doc.close()
        
        # Get suggested config and confidence report
        filename = Path(pdf_path).name
        config, confidence_report = suggest_config_settings(text, filename)
        
        # Extract data using patterns
        results = {}
        confidence_points = 0
        
        # Handle invoice number from filename if not found in text
        if confidence_report['invoice_number']['success']:
            results['invoice_number'] = confidence_report['invoice_number']['sample_matches'][0]
            confidence_points += 1
        
        # Extract other fields from text
        for field, pattern in config['patterns'].items():
            if field != 'invoice_number' or field not in results:  # Skip invoice_number if already found
                match = re.search(pattern, text)
                if match:
                    results[field] = match.group(1)
                    confidence_points += 1
                    print(f"Found {field}: {results[field]}")
        
        if len(results) >= 5:  # Allow missing one field
            # Convert amounts to float
            results['sub_total'] = float(results['sub_total'])
            results['vat_amount'] = float(results['vat_amount'])
            results['total_amount'] = float(results['total_amount'])
            
            # Set invoice date to due date if missing
            if 'invoice_date' not in results and 'due_date' in results:
                results['invoice_date'] = results['due_date']
                print("Using due date as invoice date")
            
            # Create invoice data object
            invoice_data = ValleyNorthernInvoiceData(
                **results,
                confidence_score=(confidence_points / 6) * 100
            )
            
            # Print extraction results
            print("\n=== EXTRACTION RESULTS ===")
            print(f"Invoice Number: {invoice_data.invoice_number}")
            print(f"Invoice Date: {invoice_data.invoice_date}")
            print(f"Due Date: {invoice_data.due_date}")
            print(f"Sub Total: £{invoice_data.sub_total:.2f}")
            print(f"VAT Amount: £{invoice_data.vat_amount:.2f}")
            print(f"Total Amount: £{invoice_data.total_amount:.2f}")
            print(f"Confidence Score: {invoice_data.confidence_score:.2f}%")
            
            return invoice_data
        
        return None
        
    except Exception as e:
        print(f"Error extracting data: {str(e)}")
        return None

def test_valley_northern_extraction():
    """Test extraction on sample Valley Northern invoice"""
    excel_path = Path(r"C:\Users\JulianMitchell\OneDrive - Cornwells Chemists Limited\Jasper\AI PROGAMMES\INVOICE_PROJECT\Invoice_Summary.xlsx")
    
    try:
        # Find Valley Northern sheet
        xl = pd.ExcelFile(excel_path)
        vn_sheet = None
        for sheet_name in xl.sheet_names:
            if 'valley northern' in sheet_name.lower():
                vn_sheet = sheet_name
                break
        
        if not vn_sheet:
            print("Valley Northern sheet not found")
            return
        
        # Read the sheet
        df = pd.read_excel(xl, vn_sheet)
        
        # Show available files
        print("\nAvailable Valley Northern files:")
        for index, row in df.head(10).iterrows():
            print(f"{index + 1}. {Path(row['Full Path']).name}")
        
        # Get file selection
        file_index = int(input("\nEnter the number of the file to analyze (1-10): ")) - 1
        if 0 <= file_index < len(df):
            selected_path = df.iloc[file_index]['Full Path']
            print(f"\nAnalyzing invoice: {selected_path}")
            
            result = extract_valley_northern_data(selected_path)
            if not result:
                print("\nFailed to extract data from invoice")
            
        else:
            print("Invalid file selection")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_valley_northern_extraction()