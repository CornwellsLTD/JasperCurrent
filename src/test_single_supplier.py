import fitz
import pandas as pd
from pathlib import Path

def analyze_invoice_structure(pdf_path: str):
    """Show raw text and layout of PDF"""
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text()
        doc.close()
        
        print("\n=== DOCUMENT TYPE ANALYSIS ===")
        print(f"File: {Path(pdf_path).name}")
        print("=" * 50)
        
        print("\n=== FULL TEXT ===")
        print(text)
        print("=" * 50)
        
        print("\n=== LAYOUT ANALYSIS ===")
        print("\nText Blocks by Position:\n")
        doc = fitz.open(pdf_path)
        blocks = doc[0].get_text("blocks")
        doc.close()
        
        for block in blocks:
            print(f"\nBlock at ({block[0]:.1f}, {block[1]:.1f}):")
            print(f"Text: {block[4]}\n")
        
    except Exception as e:
        print(f"Error analyzing PDF: {str(e)}")

def test_aah_extraction():
    excel_path = r"C:\Users\JulianMitchell\OneDrive - Cornwells Chemists Limited\Jasper\AI PROGAMMES\INVOICE_PROJECT\Invoice_Summary.xlsx"
    
    try:
        # Show all available sheets
        xl = pd.ExcelFile(excel_path)
        print("\nAvailable sheets in Excel file:")
        for i, sheet_name in enumerate(xl.sheet_names, 1):
            print(f"{i}. {sheet_name}")
        
        # Get sheet selection from user
        sheet_index = int(input("\nEnter the number of the sheet to analyze: ")) - 1
        if 0 <= sheet_index < len(xl.sheet_names):
            selected_sheet = xl.sheet_names[sheet_index]
            print(f"\nAnalyzing sheet: {selected_sheet}")
            
            # Read the sheet
            df = pd.read_excel(xl, selected_sheet)
            
            # Filter for unprocessed files
            unprocessed_files = df[
                (df['Invoice Date'].isna()) | 
                (df['Total Amount'].isna())
            ]
            
            if unprocessed_files.empty:
                print("No unprocessed files found in this sheet")
                return
            
            # Show available files
            print("\nAvailable unprocessed files:")
            for index, row in unprocessed_files.head(10).iterrows():
                print(f"{index + 1}. {Path(row['Full Path']).name}")
            
            # Get file selection from user
            file_index = int(input("\nEnter the number of the file to analyze (1-10): ")) - 1
            if 0 <= file_index < len(unprocessed_files):
                selected_path = unprocessed_files.iloc[file_index]['Full Path']
                print(f"\nAnalyzing invoice: {selected_path}")
                analyze_invoice_structure(selected_path)
            else:
                print("Invalid file selection")
        else:
            print("Invalid sheet selection")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_aah_extraction()