import random
from pathlib import Path
import pandas as pd
import sys
import fitz
import re
from typing import List

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Now we can import from supplier_configs
from supplier_configs.supplier_configs import SupplierConfigManager

def get_random_invoices(supplier_code: str, count: int = 20) -> List[str]:
    """Get random invoice paths for a supplier"""
    excel_path = project_root / "Invoice_Summary.xlsx"
    xl = pd.ExcelFile(excel_path)
    
    # Find supplier sheet
    supplier_sheet = None
    for sheet_name in xl.sheet_names:
        if supplier_code.lower() in sheet_name.lower():
            supplier_sheet = sheet_name
            break
    
    if not supplier_sheet:
        raise ValueError(f"Sheet not found for {supplier_code}")
    
    # Get random invoices
    df = pd.read_excel(xl, supplier_sheet)
    invoice_paths = df['Full Path'].dropna().tolist()
    return random.sample(invoice_paths, min(count, len(invoice_paths)))

def validate_config(supplier_code: str, config_dict: dict) -> bool:
    """Validate proposed config on random invoices"""
    invoice_paths = get_random_invoices(supplier_code)
    
    print(f"\nTesting configuration on {len(invoice_paths)} random invoices...")
    successes = 0
    
    for path in invoice_paths:
        print(f"\nProcessing invoice: {path}")
        # Extract text from PDF
        doc = fitz.open(path)
        text = doc[0].get_text()
        doc.close()
        
        # Test extraction with proposed config
        results = {}
        for field, pattern in config_dict['patterns'].items():
            match = re.search(pattern, text)
            if match:
                results[field] = match.group(1)
                print(f"Found {field}: {results[field]}")
            else:
                print(f"Failed to find {field}")
                print(f"Pattern used: {pattern}")  # Print the pattern that failed
        
        if len(results) == 5:  # All fields found
            successes += 1
            print("Successfully extracted all fields!")
        else:
            print(f"Failed to extract all fields. Found {len(results)}/5 fields")
    
    success_rate = (successes / len(invoice_paths)) * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    return input("\nSave this configuration? (y/n): ").lower() == 'y'

def update_supplier_config(supplier_code: str, config_dict: dict):
    """Update supplier configuration if validated"""
    manager = SupplierConfigManager()
    if supplier_code in manager.configs:
        # Update existing config
        current_config = manager.configs[supplier_code]
        for key, value in config_dict.items():
            setattr(current_config, key, value)
    else:
        # Create new config
        manager.configs[supplier_code] = config_dict
    
    manager.save_configs()
    print(f"\nConfiguration updated for {supplier_code}")

if __name__ == "__main__":
    supplier_code = input("Enter supplier code: ").upper()
    
    print("\nPaste the suggested configuration from refine_supplier_targeting.py")
    print("Enter 'END' on a new line when finished:")
    
    config_lines = []
    while True:
        line = input()
        if line == 'END':
            break
        config_lines.append(line)
    
    config_dict = eval('\n'.join(config_lines))
    
    if validate_config(supplier_code, config_dict):
        update_supplier_config(supplier_code, config_dict)