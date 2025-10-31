#!/usr/bin/env python3
"""
Script to fix pattern structure inconsistencies
"""

import json
import os
import sys
from pathlib import Path


def fix_pattern_structure(file_path):
    """Fix pattern structure inconsistencies in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fix subcategory positioning - check if it exists anywhere in the file
        if 'subcategory' in data:
            # Save the subcategory value
            subcategory_value = data['subcategory']
            
            # Create a new ordered dictionary with proper field order
            new_data = {}
            
            # Add all fields in the correct order
            field_order = ['vendor', 'vendor_id', 'product', 'product_id', 'category', 'subcategory']
            for field in field_order:
                if field in data:
                    if field == 'subcategory':
                        new_data[field] = subcategory_value
                    else:
                        new_data[field] = data[field]
            
            # Add remaining fields
            for key, value in data.items():
                if key not in field_order:
                    new_data[key] = value
            
            data = new_data
        
        # Remove category/subcategory/vendor/product from individual patterns in all_versions
        if 'all_versions' in data and isinstance(data['all_versions'], list):
            for pattern in data['all_versions']:
                if isinstance(pattern, dict):
                    # Remove fields that should only be at top level
                    fields_to_remove = ['category', 'subcategory', 'vendor', 'product']
                    for field in fields_to_remove:
                        if field in pattern:
                            del pattern[field]
        
        # Remove category/subcategory/vendor/product from individual patterns in versions
        if 'versions' in data and isinstance(data['versions'], dict):
            for version, patterns in data['versions'].items():
                if isinstance(patterns, list):
                    for pattern in patterns:
                        if isinstance(pattern, dict):
                            # Remove fields that should only be at top level
                            fields_to_remove = ['category', 'subcategory', 'vendor', 'product']
                            for field in fields_to_remove:
                                if field in pattern:
                                    del pattern[field]
        
        # Write the fixed data back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Fixed structure: {file_path}")
        return True
    
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def fix_all_patterns(patterns_dir):
    """Fix all pattern files in a directory"""
    fixed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                if fix_pattern_structure(file_path):
                    fixed_count += 1
                else:
                    error_count += 1
    
    print(f"\nSummary: {fixed_count} files fixed, {error_count} errors")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        patterns_dir = sys.argv[1]
    else:
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
    
    if not os.path.exists(patterns_dir):
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)
    
    fix_all_patterns(patterns_dir)