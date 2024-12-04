import os
import sys
from pathlib import Path
import fitz
import pandas as pd
import logging
import re
from datetime import datetime

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add project root to Python path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import the modules
from supplier_configs.supplier_configs import SupplierConfigManager
from utils.logging_utils import InvoiceProcessingLogger

def process_supplier_invoices(supplier_code: str, excel_path: Path):
    """Process all invoices for a specific supplier"""
    # Initialize config manager
    config_manager = SupplierConfigManager()
    
    if supplier_code not in config_manager.configs:
        print(f"Error: Unknown supplier code '{supplier_code}'")
        return
    
    config = config_manager.configs[supplier_code]
    logger = InvoiceProcessingLogger(config.name)
    
    try:
        print(f"\nStarting processing for {config.name}")
        start_time = datetime.now()
        
        # Load Excel file
        xl = pd.ExcelFile(excel_path)
        supplier_sheet = None
        
        # Find supplier sheet
        for sheet_name in xl.sheet_names:
            if config.sheet_identifier in sheet_name.lower():
                supplier_sheet = sheet_name
                break
        
        if not supplier_sheet:
            print(f"Sheet not found for {config.name}")
            return
        
        # Process files
        df = pd.read_excel(xl, supplier_sheet)
        total_files = len(df)
        successful_updates = 0
        print(f"Found {total_files} files to process")
        
        for index, row in df.iterrows():
            file_path = row['Full Path']
            
            try:
                # Skip if already processed
                if pd.notna(row['Invoice Date']) and pd.notna(row['Total Amount']):
                    print(f"Skipping already processed file: {Path(file_path).name}")
                    continue
                
                print(f"\nProcessing {index + 1}/{total_files}: {Path(file_path).name}")
                
                # Extract data using supplier-specific patterns
                doc = fitz.open(file_path)
                text = doc[0].get_text()
                doc.close()
                
                # Check validation markers
                if not all(marker in text for marker in config.validation_markers):
                    print(f"Skipping invalid file: {Path(file_path).name}")
                    continue
                
                if any(marker in text for marker in config.exclusion_markers):
                    print(f"Skipping excluded file: {Path(file_path).name}")
                    continue
                
                # Extract data using patterns
                data = {}
                confidence_points = 0
                total_checks = len(config.patterns)
                
                filename = Path(file_path).name
                for field, pattern in config.patterns.items():
                    # Check filename patterns first
                    if field in ['invoice_number', 'reference_number']:
                        match = re.search(pattern, filename)
                    else:
                        match = re.search(pattern, text)
                    
                    if match:
                        data[field] = match.group(1)
                        confidence_points += 1
                
                confidence_score = (confidence_points / total_checks) * 100
                
                # Define column mapping
                column_mapping = {
                    'invoice_number': 'Invoice/Tax Point Number',
                    'invoice_date': 'Invoice Date',
                    'reference_number': 'Reference Number',
                    'pre_vat_total': 'Pre-VAT Total',
                    'total_amount': 'Total Amount'
                }

                if confidence_score >= config.high_confidence_threshold:
                    # Update DataFrame using column mapping
                    for field, value in data.items():
                        excel_column = column_mapping.get(field)
                        if excel_column and excel_column in df.columns:
                            df.at[index, excel_column] = value
                        else:
                            print(f"Warning: Column '{excel_column}' not found in Excel sheet")
                    successful_updates += 1
                    print(f"Successfully updated data for {Path(file_path).name}")
                
                # Save progress every 10 files
                if (index + 1) % 10 == 0:
                    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', 
                                      if_sheet_exists='replace') as writer:
                        df.to_excel(writer, sheet_name=supplier_sheet, index=False)
                    print(f"Progress saved after {index + 1} files")
                
            except Exception as e:
                print(f"Error processing {Path(file_path).name}: {str(e)}")
        
        # Final save
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', 
                           if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=supplier_sheet, index=False)
        
        # Update configuration statistics
        stats = {
            'run_date': start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_processed': total_files,
            'success_rate': (successful_updates / total_files) * 100 if total_files > 0 else 0
        }
        config_manager.update_config_stats(supplier_code, stats)
        
        # Just before the final print statements, add this debug section:
        print("\n" + "="*50)
        print("DEBUG SUMMARY")
        print("="*50)

        print("\nConfiguration Used:")
        print(f"Name: {config.name}")
        print(f"Sheet identifier: {config.sheet_identifier}")
        print(f"Validation markers: {config.validation_markers}")
        print(f"Exclusion markers: {config.exclusion_markers}")
        print("\nPatterns:")
        for field, pattern in config.patterns.items():
            print(f"  {field}: {pattern}")

        print("\nExcel Column Mapping:")
        for field, excel_col in column_mapping.items():
            if excel_col in df.columns:
                print(f"✓ {field} -> {excel_col}")
            else:
                print(f"✗ {field} -> {excel_col} (not found)")

        print("\nProcessing Statistics:")
        print(f"Total files found: {total_files}")
        print(f"Files skipped (already processed): {sum(1 for _, row in df.iterrows() if pd.notna(row['Invoice Date']) and pd.notna(row['Total Amount']))}")
        print(f"Files skipped (validation markers): {sum(1 for _, row in df.iterrows() if not all(marker in text for marker in config.validation_markers))}")
        print(f"Files skipped (exclusion markers): {sum(1 for _, row in df.iterrows() if any(marker in text for marker in config.exclusion_markers))}")
        print(f"Files processed: {total_files - successful_updates}")
        print(f"Successful updates: {successful_updates}")
        print(f"Success rate: {(successful_updates/total_files)*100 if total_files > 0 else 0:.2f}%")

        print("\n" + "="*50)
        print("END DEBUG SUMMARY")
        print("="*50)

        # Then continue with your existing final summary
        print(f"\nProcessing completed for {config.name}")
        print(f"Total files processed: {total_files}")
        print(f"Successfully updated: {successful_updates}")
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    # Initialize config manager
    config_manager = SupplierConfigManager()
    
    # Show available suppliers
    print("\nAvailable suppliers:")
    for code in config_manager.configs.keys():
        print(f"- {code}")
    
    # Get supplier code from user
    supplier_code = input("\nEnter supplier code from the list above: ").upper()
    
    excel_path = Path(r"C:\Users\JulianMitchell\OneDrive - Cornwells Chemists Limited\Jasper\AI PROGAMMES\INVOICE_PROJECT\Invoice_Summary.xlsx")
    
    process_supplier_invoices(supplier_code, excel_path)
    