#!/usr/bin/env python3
"""
Search for patterns by vendor or product in the new by-vendor structure
"""

import os
import json
import sys
import re


def search_patterns(patterns_dir, search_term):
    """Search for patterns by vendor or product name"""
    by_vendor_dir = os.path.join(patterns_dir, 'by-vendor')
    
    if not os.path.exists(by_vendor_dir):
        print("Error: by-vendor directory not found")
        return
    
    print(f"Searching for patterns matching '{search_term}':")
    print("=" * 50)
    
    matches = []
    
    # Walk through vendor directories
    for vendor in os.listdir(by_vendor_dir):
        vendor_path = os.path.join(by_vendor_dir, vendor)
        
        if not os.path.isdir(vendor_path) or vendor == 'README.md':
            continue
        
        # Check if vendor name matches
        if re.search(search_term, vendor, re.IGNORECASE):
            matches.append(('vendor', vendor, vendor_path))
        
        # Check product files
        for product_file in os.listdir(vendor_path):
            if not product_file.endswith('.json'):
                continue
                
            product_path = os.path.join(vendor_path, product_file)
            
            try:
                with open(product_path, 'r') as f:
                    data = json.load(f)
                
                product_name = data.get('product', '')
                category = data.get('category', '')
                
                # Check if product name matches
                if re.search(search_term, product_name, re.IGNORECASE):
                    matches.append(('product', f"{vendor}/{product_name} ({category})", product_path))
                    
            except Exception as e:
                print(f"Error reading {product_path}: {e}")
    
    # Display matches
    if matches:
        for match_type, name, path in matches:
            print(f"{match_type.capitalize()}: {name}")
            print(f"  Path: {path}")
            
            # Show pattern count for products
            if match_type == 'product':
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                    
                    all_versions_count = len(data.get('all_versions', []))
                    version_patterns_count = 0
                    versions = data.get('versions', {})
                    for version_patterns_list in versions.values():
                        version_patterns_count += len(version_patterns_list)
                    
                    print(f"  Patterns: {all_versions_count + version_patterns_count}")
                except Exception as e:
                    print(f"  Error reading pattern count: {e}")
            
            print()
    else:
        print("No matches found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python search-patterns.py <search-term>")
        sys.exit(1)
    
    search_term = sys.argv[1]
    
    # Define paths
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    patterns_dir = os.path.join(workspace_dir, 'patterns')
    
    search_patterns(patterns_dir, search_term)