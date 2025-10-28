#!/usr/bin/env python3
"""
Script to check for duplicate patterns in the repository
"""

import json
import os
import hashlib
from collections import defaultdict


def calculate_pattern_hash(pattern_data):
    """
    Calculate a hash for a pattern based on its key characteristics.
    
    Args:
        pattern_data (dict): Pattern data
        
    Returns:
        str: Hash of the pattern
    """
    # Extract key fields for comparison
    key_fields = {
        'name': pattern_data.get('name', ''),
        'pattern': pattern_data.get('pattern', ''),
        'vendor': pattern_data.get('vendor', ''),
        'product': pattern_data.get('product', '')
    }
    
    # Create a string representation and hash it
    pattern_str = json.dumps(key_fields, sort_keys=True)
    return hashlib.md5(pattern_str.encode('utf-8')).hexdigest()


def find_duplicate_patterns(patterns_dir):
    """
    Find duplicate patterns in the repository.
    
    Args:
        patterns_dir (str): Directory containing pattern files
    """
    # Dictionary to store pattern hashes
    pattern_hashes = defaultdict(list)
    
    # Walk through all pattern files
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Handle both single pattern files and multi-version files
                    if 'all_versions' in data:
                        patterns = data['all_versions']
                    else:
                        patterns = [data]
                    
                    # Calculate hash for each pattern
                    for pattern in patterns:
                        pattern_hash = calculate_pattern_hash(pattern)
                        pattern_hashes[pattern_hash].append({
                            'file': filepath,
                            'pattern_name': pattern.get('name', 'Unknown')
                        })
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    # Report duplicates
    duplicates_found = 0
    for pattern_hash, pattern_list in pattern_hashes.items():
        if len(pattern_list) > 1:
            duplicates_found += 1
            print(f"\nDuplicate group (hash: {pattern_hash[:8]}):")
            for pattern_info in pattern_list:
                print(f"  - {pattern_info['pattern_name']} in {pattern_info['file']}")
    
    print(f"\nFound {duplicates_found} groups of duplicate patterns")


def main():
    """Main function."""
    patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
    
    if not os.path.exists(patterns_dir):
        print(f"Patterns directory not found: {patterns_dir}")
        return
    
    print("Checking for duplicate patterns...")
    find_duplicate_patterns(patterns_dir)
    
    print("Duplicate check completed!")


if __name__ == "__main__":
    main()