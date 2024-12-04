import os
import sys
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from supplier_configs.supplier_configs import SupplierConfigManager

def refresh_configs():
    manager = SupplierConfigManager()
    print("\nLoading default configs...")
    default_configs = manager._get_default_configs()
    
    # Print ALLIANCE config details
    alliance_config = default_configs['ALLIANCE']
    print("\nALLIANCE Configuration:")
    print(f"Validation Markers: {alliance_config.validation_markers}")
    print(f"Exclusion Markers: {alliance_config.exclusion_markers}")
    print(f"Patterns: {json.dumps(alliance_config.patterns, indent=2)}")
    
    print("\nSaving configs...")
    manager.configs = default_configs
    manager.save_configs()
    
    print("\nVerifying saved configs...")
    with open(manager.config_file, 'r') as f:
        saved_config = json.load(f)
        print(f"ALLIANCE validation markers in saved file: {saved_config['ALLIANCE']['validation_markers']}")
    
    print("\nConfiguration refreshed!")
    print("\nAvailable suppliers:")
    for code in manager.configs.keys():
        print(f"- {code}")

if __name__ == "__main__":
    refresh_configs() 