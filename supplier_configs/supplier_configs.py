# supplier_configs.py
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime

@dataclass
class SupplierConfig:
    code: str
    name: str
    sheet_identifier: str
    validation_markers: List[str]
    exclusion_markers: List[str]
    patterns: dict
    high_confidence_threshold: float = 95.0
    review_confidence_threshold: float = 75.0
    last_run_date: str = ""
    total_processed: int = 0
    success_rate: float = 0.0
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class SupplierConfigManager:
    def __init__(self):
        self.config_dir = Path("supplier_configs")
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "supplier_configs.json"
        self.configs = self._load_configs()
    
    def _load_configs(self) -> Dict[str, SupplierConfig]:
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                return {code: SupplierConfig.from_dict(data) 
                       for code, data in config_data.items()}
        return self._get_default_configs()
    
    def _get_default_configs(self) -> Dict[str, SupplierConfig]:
        configs = {
            "ABBOTT": SupplierConfig(
                code="ABBOTT",
                name="Abbott Laboratories Limited",
                sheet_identifier="abbott",
                validation_markers=["ABBOTT LABORATORIES LIMITED", "INVOICE"],
                exclusion_markers=["REMITTANCE ADVICE"],
                patterns={
                    "invoice_number": r"Invoice No\.?\s*(\d{7})",
                    "invoice_date": r"Invoice Date\s*(\d{2}/\d{2}/\d{4})",
                    "reference_number": r"Account Ref No\.\s*(\d+)",
                    "pre_vat_total": r"Total Net Amount\s*([\d,]+\.\d{2})",
                    "total_amount": r"Invoice Total\s*([\d,]+\.\d{2})"
                }
            ),
            "AJBELL": SupplierConfig(
                code="AJBELL",
                name="AJ Bell Business Solutions Limited",
                sheet_identifier="bell",
                validation_markers=["AJ Bell", "FEE INVOICE"],
                exclusion_markers=["REMITTANCE"],
                patterns={
                    "invoice_number": r"Invoice Number:\s*(\d{2}/\d{2}/\d{3})",
                    "invoice_date": r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
                    "reference_number": r"Our Ref:\s*(CORN\d{4})",
                    "pre_vat_total": r"Total Fee:\s*£([\d,]+\.\d{2})",
                    "total_amount": r"Total Invoice:\s*£([\d,]+\.\d{2})"
                }
            ),
            "ADEPT": SupplierConfig(
                code="ADEPT",
                name="Adept Computer Support Ltd",
                sheet_identifier="adept",
                validation_markers=["Adept Computer Support Ltd", "Invoice"],
                exclusion_markers=["REMITTANCE", "Statement"],
                patterns={
                    'invoice_number': r"\b(\d{5})\b(?=\s*\d{2}/\d{2}/\d{4})",
                    'invoice_date': r"\b(\d{2}/\d{2}/\d{4})\b",
                    'reference_number': r"Serial:\s*(ITACS\d{4})",
                    'pre_vat_total': r"Sub Total\s*(\d+\.\d{2})",
                    'total_amount': r"Invoice Total\s*(\d+\.\d{2})"
                }
            ),
            "ASH_WASTE": SupplierConfig(
                code="ASH_WASTE",
                name="ASH Waste Services Ltd",
                sheet_identifier="ash waste",
                validation_markers=["ASH Waste Services Ltd"],
                exclusion_markers=["REMITTANCE", "Statement"],
                patterns={
                    'invoice_number': r"INV(\d+)_\d+\.pdf",
                    'invoice_date': r"\b(\d{2}/\d{2}/\d{4})\b",
                    'reference_number': r"INV\d+_(\d+)\.pdf",
                    'pre_vat_total': r"VAT\s*£(\d+\.\d{2})",
                    'total_amount': r"£\d+\.\d{2}\s*£\d+\.\d{2}\s*£(\d+\.\d{2})"
                },
                high_confidence_threshold=95.0,
                review_confidence_threshold=75.0,
                last_run_date="",
                total_processed=0,
                success_rate=0.0
            ),
            "ALLIANCE": SupplierConfig(
                code="ALLIANCE",
                name="Alliance Healthcare (Distribution) Ltd",
                sheet_identifier="alliance",
                validation_markers=[
                    'Alliance Healthcare',
                    'STATEMENT'
                ],
                exclusion_markers=[
                    'NO OUTSTANDING ITEMS',
                    'SUPPRESS'
                ],
                patterns={
                    'invoice_number': r"(\d+)_([A-Z0-9]+)_(\d{2}-\d{2}-\d{4})\.pdf",
                    'invoice_date': r"(\d{2}APR\d{2})\s+1",
                    'reference_number': r"(\d+)_[A-Z0-9]+_\d{2}-\d{2}-\d{4}\.pdf",
                    'pre_vat_total': r"PAGE TOTAL\s+(\d+\.\d{2})",
                    'total_amount': r"INVOICE TOTAL\s+(\d+\.\d{2})"
                },
                high_confidence_threshold=95.0,
                review_confidence_threshold=75.0,
                last_run_date="",
                total_processed=0,
                success_rate=0.0
            ),
            "VALLEY": SupplierConfig(
                code="VALLEY",
                name="Valley Northern",
                sheet_identifier="valley northern",
                validation_markers=[
                    'Valley Northern Ltd',
                    'INVOICE FOR'
                ],
                exclusion_markers=[
                    'STATEMENT',
                    'CREDIT NOTE'
                ],
                patterns={
                    'invoice_number': r'Invoice\s*Date\s*Invoice\s*No[\s\S]{0,200}?(\d{5,7})',
                    'invoice_date': r'Invoice\s*Date\s*Invoice\s*No[\s\S]{0,100}?(\d{2}/\d{2}/\d{4})',
                    'reference_number': r'(?:Customer\s*Order\s*Number[\s\S]{0,200}?\([\s\S]*?([\w\-]+)\)|VN\d{5})',
                    'pre_vat_total': r'Sub\s*Total[\s\S]{0,50}?(\d+\.\d{2})',
                    'total_amount': r'(?:TOTAL\s*DUE\s*\(£\)|TOTAL\s*AMOUNT)[\s\S]{0,50}?(\d+\.\d{2})'
                },
                high_confidence_threshold=95.0,
                review_confidence_threshold=75.0,
                last_run_date="",
                total_processed=0,
                success_rate=0.0
            )
        }
        return configs
    
    def save_configs(self):
        config_data = {code: config.to_dict() 
                      for code, config in self.configs.items()}
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
    
    def update_config_stats(self, code: str, stats: dict):
        if code in self.configs:
            config = self.configs[code]
            config.last_run_date = stats['run_date']
            config.total_processed = stats['total_processed']
            config.success_rate = stats['success_rate']
            self.save_configs()