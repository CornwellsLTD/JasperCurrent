# utils/logging_utils.py
import logging
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

class InvoiceProcessingLogger:
    def __init__(self, supplier_name: str):
        # Set up logging directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create supplier-specific log directory
        self.supplier_dir = self.log_dir / supplier_name
        self.supplier_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = self.setup_logger()
        
        # Initialize statistics
        self.stats = {
            'total_processed': 0,
            'successful_updates': 0,
            'skipped_files': 0,
            'review_needed': 0,
            'errors': 0,
            'failed_files': []
        }
    
    def setup_logger(self):
        # Create a new logger instance
        logger = logging.getLogger(f"invoice_processor_{self.timestamp}")
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate logging
        if not logger.handlers:
            # Create file handler
            log_file = self.supplier_dir / f"processing_{self.timestamp}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    # Logging methods
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
        
    def debug(self, message: str):
        self.logger.debug(message)
    
    def log_failed_file(self, filename: str, reason: str):
        """Log a failed file with its reason"""
        self.stats['failed_files'].append((filename, reason))
        self.warning(f"Failed to process {filename}: {reason}")
    
    def log_successful_file(self, filename: str):
        """Log a successfully processed file"""
        self.stats['successful_updates'] += 1
        self.info(f"Successfully processed: {filename}")
    
    def generate_summary(self):
        """Generate and log processing summary"""
        self.info("\n=== Processing Summary ===")
        self.info(f"Total files processed: {self.stats['total_processed']}")
        self.info(f"Successfully updated: {self.stats['successful_updates']}")
        self.info(f"Failed files: {len(self.stats['failed_files'])}")
        
        if self.stats['failed_files']:
            self.info("\nFailed Files Details:")
            for filename, reason in self.stats['failed_files']:
                self.info(f"❌ {filename}: {reason}")