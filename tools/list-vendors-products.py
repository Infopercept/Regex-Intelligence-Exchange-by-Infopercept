#!/usr/bin/env python3
"""
List all vendors and products in the new by-vendor structure
"""

import os
import json
from pathlib import Path


def list_vendors_products(patterns_dir):
    """List all vendors and products in the by-vendor structure"""
    by_vendor_dir = os.path.join(patterns_dir, 'by-vendor')
    
    if not os.path.exists(by_vendor_dir):
        print("Error: by-vendor directory not found")
        return
    
    print("Vendors and Products in by-vendor structure:")
    print("=" * 50)
    
    # Get all vendor directories
    vendors = [d for d in os.listdir(by_vendor_dir) 
               if os.path.isdir(os.path.join(by_vendor_dir, d)) and d != 'README.md']
    
    # Sort vendors alphabetically
    vendors.sort()
    
    for vendor in vendors:
        vendor_path = os.path.join(by_vendor_dir, vendor)
        print(f"\n{vendor}:")
        
        # Get all product files for this vendor
        products = [f for f in os.listdir(vendor_path) if f.endswith('.json')]
        products.sort()
        
        for product in products:
            product_path = os.path.join(vendor_path, product)
            try:
                with open(product_path, 'r') as f:
                    data = json.load(f)
                
                product_name = data.get('product', 'Unknown')
                category = data.get('category', 'Unknown')
                pattern_count = len(data.get('all_versions', []))
                
                # Count version-specific patterns
                version_patterns = 0
                versions = data.get('versions', {})
                for version_patterns_list in versions.values():
                    version_patterns += len(version_patterns_list)
                
                print(f"  - {product_name} ({category}) - {pattern_count + version_patterns} patterns")
            except Exception as e:
                print(f"  - {product} (Error reading file: {e})")


if __name__ == "__main__":
    # Define paths
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    patterns_dir = os.path.join(workspace_dir, 'patterns')
    
    list_vendors_products(patterns_dir)