import os
import pandas as pd
from pathlib import Path
import openpyxl

def clean_sheet_name(name):
    invalid_chars = ['[', ']', ':', '*', '?', '/', '\\']
    clean_name = ''.join(char for char in name if char not in invalid_chars)
    return clean_name[:31]

def get_existing_data(excel_path):
    """Read existing data from Excel file if it exists"""
    existing_data = {}
    if excel_path.exists():
        try:
            xl = pd.ExcelFile(excel_path)
            for sheet_name in xl.sheet_names:
                if sheet_name != 'Summary':
                    df = pd.read_excel(xl, sheet_name)
                    # Create dictionary with Full Path as key and row data as value
                    sheet_data = {}
                    for _, row in df.iterrows():
                        if pd.notna(row['Full Path']):  # Only store if Full Path exists
                            sheet_data[row['Full Path']] = {
                                'Invoice Date': row['Invoice Date'],
                                'Invoice/Tax Point Number': row['Invoice/Tax Point Number'],
                                'Reference Number': row['Reference Number'],
                                'Pre-VAT Total': row['Pre-VAT Total'],
                                'Total Amount': row['Total Amount']
                            }
                    existing_data[sheet_name] = sheet_data
            print("Successfully loaded existing data")
        except Exception as e:
            print(f"Warning: Could not load existing data: {str(e)}")
    return existing_data

def create_invoice_summary(root_path, output_path):
    root_dir = Path(root_path)
    output_dir = Path(output_path)
    excel_path = output_dir / 'Invoice_Summary.xlsx'
    
    # Get existing data before creating new data
    existing_data = get_existing_data(excel_path)
    
    summary_data = []
    all_dfs = {}
    supplier_code_counter = 1
    
    for supplier_folder in root_dir.iterdir():
        if supplier_folder.is_dir():
            supplier_code = f"SUP{supplier_code_counter:04d}"
            supplier_code_counter += 1
            invoice_data = []
            sheet_name = clean_sheet_name(supplier_folder.name)
            
            for pdf_file in supplier_folder.rglob('*.pdf'):
                # Get existing values if available
                existing_values = {'Invoice Date': '', 
                                 'Invoice/Tax Point Number': '',
                                 'Reference Number': '',
                                 'Pre-VAT Total': '',
                                 'Total Amount': ''}
                
                if sheet_name in existing_data and str(pdf_file) in existing_data[sheet_name]:
                    existing_values = existing_data[sheet_name][str(pdf_file)]
                
                invoice_data.append({
                    'Invoice File': pdf_file.name,
                    'Invoice Date': existing_values['Invoice Date'],
                    'Invoice/Tax Point Number': existing_values['Invoice/Tax Point Number'],
                    'Reference Number': existing_values['Reference Number'],
                    'Pre-VAT Total': existing_values['Pre-VAT Total'],
                    'Total Amount': existing_values['Total Amount'],
                    'Period Folder': pdf_file.parent.name,
                    'File Size (KB)': round(pdf_file.stat().st_size / 1024, 2),
                    'Full Path': str(pdf_file),
                    'Supplier Code': supplier_code
                })
            
            if invoice_data:
                columns = [
                    'Invoice File',
                    'Invoice Date',
                    'Invoice/Tax Point Number',
                    'Reference Number',
                    'Pre-VAT Total',
                    'Total Amount',
                    'Period Folder',
                    'File Size (KB)',
                    'Full Path',
                    'Supplier Code'
                ]
                
                df_supplier = pd.DataFrame(invoice_data, columns=columns)
                all_dfs[sheet_name] = df_supplier
                
                total_size_mb = sum(item['File Size (KB)'] for item in invoice_data) / 1024
                summary_data.append({
                    'Supplier Name': supplier_folder.name,
                    'Supplier Code': supplier_code,
                    'Invoice Count': len(invoice_data),
                    'Total Size (MB)': round(total_size_mb, 2)
                })
    
    df_summary = pd.DataFrame(summary_data)
    totals = {
        'Supplier Name': 'TOTALS',
        'Supplier Code': '',
        'Invoice Count': df_summary['Invoice Count'].sum(),
        'Total Size (MB)': round(df_summary['Total Size (MB)'].sum(), 2)
    }
    df_summary = pd.concat([df_summary, pd.DataFrame([totals])], ignore_index=True)
    
    # Write to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Write summary sheet
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Write supplier sheets
        for sheet_name, df in all_dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Format columns
            worksheet = writer.sheets[sheet_name]
            
            # Set column widths
            column_widths = {
                'A': 30,  # Invoice File
                'B': 15,  # Invoice Date
                'C': 20,  # Invoice/Tax Point Number
                'D': 20,  # Reference Number
                'E': 15,  # Pre-VAT Total
                'F': 15,  # Total Amount
                'G': 20,  # Period Folder
                'H': 15,  # File Size
                'I': 50,  # Full Path
                'J': 15   # Supplier Code
            }
            
            for col_letter, width in column_widths.items():
                worksheet.column_dimensions[col_letter].width = width
        
        # Format summary sheet
        worksheet = writer.sheets['Summary']
        summary_widths = {'A': 40, 'B': 15, 'C': 15, 'D': 15}
        for col_letter, width in summary_widths.items():
            worksheet.column_dimensions[col_letter].width = width
    
    return excel_path

if __name__ == "__main__":
    root_path = r"C:\Users\JulianMitchell\Cornwells Chemists Limited\Cornwells File Share - Documents\Head Office\Accounts\Invoices"
    output_path = r"C:\Users\JulianMitchell\OneDrive - Cornwells Chemists Limited\Jasper\AI PROGAMMES\INVOICE_PROJECT"
    
    try:
        excel_file = create_invoice_summary(root_path, output_path)
        print(f"Excel file updated successfully at: {excel_file}")
        print("Your previous entries in the editable columns have been preserved.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")