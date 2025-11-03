#!/usr/bin/env python3
"""
Script to standardize and validate all patterns in the patterns directory
"""

import os
import re
import json
from pathlib import Path

def validate_pattern_format(pattern_data):
    """Validate that a pattern follows the required format"""
    required_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category', 'all_versions']
    
    # Check required top-level fields
    for field in required_fields:
        if field not in pattern_data:
            return False, f"Missing required field: {field}"
    
    # Validate all_versions array
    if not isinstance(pattern_data['all_versions'], list):
        return False, "all_versions must be an array"
    
    # Validate each pattern in all_versions
    for i, pattern in enumerate(pattern_data['all_versions']):
        required_pattern_fields = ['name', 'pattern']
        for field in required_pattern_fields:
            if field not in pattern:
                return False, f"Pattern {i} missing required field: {field}"
        
        # Validate metadata if present
        if 'metadata' in pattern:
            metadata = pattern['metadata']
            required_metadata_fields = ['author', 'created_at', 'updated_at', 'description', 'tags']
            for field in required_metadata_fields:
                if field not in metadata:
                    return False, f"Pattern {i} metadata missing required field: {field}"
    
    return True, "Pattern format is valid"

def standardize_pattern(pattern_data):
    """Standardize a pattern to ensure consistent format"""
    # Ensure all required fields are present
    if 'versions' not in pattern_data:
        pattern_data['versions'] = {}
    
    if 'subcategory' not in pattern_data:
        pattern_data['subcategory'] = ''
    
    # Standardize all_versions patterns
    for pattern in pattern_data['all_versions']:
        # Ensure priority and confidence are present
        if 'priority' not in pattern:
            pattern['priority'] = 100
        if 'confidence' not in pattern:
            pattern['confidence'] = 0.8
            
        # Ensure metadata is present
        if 'metadata' not in pattern:
            pattern['metadata'] = {
                'author': 'Unknown',
                'created_at': '2025-01-01',
                'updated_at': '2025-01-01',
                'description': 'Pattern description',
                'tags': ['imported'],
                'source': 'Unknown',
                'license': 'MIT',
                'severity': 'low',
                'cvss_score': 0.0,
                'cwe_ids': [],
                'affected_versions': [],
                'remediation': 'Keep the software updated to the latest stable version'
            }
        
        # Ensure test_cases are present in metadata
        if 'test_cases' not in pattern['metadata']:
            pattern['metadata']['test_cases'] = []
    
    return pattern_data

def process_patterns_directory(patterns_dir):
    """Process all patterns in the directory and standardize them"""
    if not os.path.exists(patterns_dir):
        print(f"Directory {patterns_dir} does not exist")
        return
    
    # Find all JSON files recursively
    pattern_files = list(Path(patterns_dir).rglob('*.json'))
    print(f"Found {len(pattern_files)} pattern files")
    
    standardized_count = 0
    error_count = 0
    
    for pattern_file in pattern_files:
        try:
            # Load pattern data
            with open(pattern_file, 'r', encoding='utf-8') as f:
                pattern_data = json.load(f)
            
            # Validate pattern format
            is_valid, message = validate_pattern_format(pattern_data)
            if not is_valid:
                print(f"Invalid format in {pattern_file}: {message}")
                error_count += 1
                continue
            
            # Standardize pattern
            standardized_pattern = standardize_pattern(pattern_data)
            
            # Save standardized pattern
            with open(pattern_file, 'w', encoding='utf-8') as f:
                json.dump(standardized_pattern, f, indent=2, ensure_ascii=False)
            
            standardized_count += 1
            
        except Exception as e:
            print(f"Error processing {pattern_file}: {e}")
            error_count += 1
            continue
    
    print(f"Standardized {standardized_count} patterns")
    print(f"Errors: {error_count}")

if __name__ == '__main__':
    # Configuration
    PATTERNS_DIR = 'patterns/by-vendor'
    
    # Process patterns
    process_patterns_directory(PATTERNS_DIR)