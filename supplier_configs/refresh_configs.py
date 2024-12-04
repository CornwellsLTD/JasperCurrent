import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from supplier_configs.supplier_configs import SupplierConfigManager

def refresh_configs():
    manager = SupplierConfigManager()
    manager.configs = manager._get_default_configs()
    manager.save_configs()
    print("Configuration refreshed!")
    print("\nAvailable suppliers:")
    for code in manager.configs.keys():
        print(f"- {code}")

if __name__ == "__main__":
    refresh_configs()