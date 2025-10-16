#!/usr/bin/env python3
"""
Validation script to validate all pattern files in the repository
"""

import json
import os
import re
import sys
from pathlib import Path


def find_pattern_files(root_dir):
    """Find all pattern files in the repository."""
    pattern_files = []
    patterns_dir = os.path.join(root_dir, 'patterns')
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                pattern_files.append(os.path.join(root, file))
    
    return pattern_files


def validate_pattern_file(file_path):
    """Validate a single pattern file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check required top-level fields
        required_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category']
        for field in required_fields:
            if field not in data:
                print(f"Error: Missing required field '{field}' in {file_path}")
                return False
        
        # Check versions structure
        if 'versions' in data:
            if not isinstance(data['versions'], dict):
                print(f"Error: 'versions' must be an object in {file_path}")
                return False
            
            for version, patterns in data['versions'].items():
                if not isinstance(patterns, list):
                    print(f"Error: 'versions.{version}' must be an array in {file_path}")
                    return False
                
                for pattern in patterns:
                    if not validate_pattern_structure(pattern, file_path):
                        return False
        
        # Check all_versions structure
        if 'all_versions' in data:
            if not isinstance(data['all_versions'], list):
                print(f"Error: 'all_versions' must be an array in {file_path}")
                return False
            
            for pattern in data['all_versions']:
                if not validate_pattern_structure(pattern, file_path):
                    return False
        
        return True
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error validating {file_path}: {e}")
        return False


def validate_pattern_structure(pattern, file_path):
    """Validate the structure of a single pattern."""
    # Check required fields
    required_fields = ['name', 'pattern', 'priority', 'confidence']
    for field in required_fields:
        if field not in pattern:
            print(f"Error: Missing required field '{field}' in pattern in {file_path}")
            return False
    
    # Validate pattern is a valid regex
    try:
        re.compile(pattern['pattern'])
    except re.error as e:
        print(f"Error: Invalid regex pattern '{pattern['pattern']}' in {file_path}: {e}")
        return False
    
    # Validate priority is between 0 and 200
    if not isinstance(pattern['priority'], int) or pattern['priority'] < 0 or pattern['priority'] > 200:
        print(f"Error: priority must be an integer between 0 and 200 in {file_path}")
        return False
    
    # Validate confidence is between 0.0 and 1.0
    if not isinstance(pattern['confidence'], (int, float)) or pattern['confidence'] < 0.0 or pattern['confidence'] > 1.0:
        print(f"Error: confidence must be a number between 0.0 and 1.0 in {file_path}")
        return False
    
    # Validate metadata if present
    if 'metadata' in pattern:
        if not isinstance(pattern['metadata'], dict):
            print(f"Error: metadata must be an object in {file_path}")
            return False
        
        # Check required metadata fields
        required_metadata_fields = ['author', 'created_at', 'updated_at', 'description', 'tags']
        for field in required_metadata_fields:
            if field not in pattern['metadata']:
                print(f"Error: Missing required metadata field '{field}' in {file_path}")
                return False
        
        # Validate tags is an array
        if not isinstance(pattern['metadata']['tags'], list):
            print(f"Error: metadata.tags must be an array in {file_path}")
            return False
        
        # Validate test_cases if present
        if 'test_cases' in pattern['metadata']:
            if not isinstance(pattern['metadata']['test_cases'], list):
                print(f"Error: metadata.test_cases must be an array in {file_path}")
                return False
            
            for test_case in pattern['metadata']['test_cases']:
                if not isinstance(test_case, dict):
                    print(f"Error: Each test case must be an object in {file_path}")
                    return False
                
                if 'input' not in test_case or 'expected_version' not in test_case:
                    print(f"Error: Test cases must have 'input' and 'expected_version' fields in {file_path}")
                    return False
    
    return True


def main():
    """Main function."""
    # Get the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    print("Validating all pattern files...")
    
    # Find all pattern files
    pattern_files = find_pattern_files(repo_root)
    
    if not pattern_files:
        print("No pattern files found!")
        return 1
    
    print(f"Found {len(pattern_files)} pattern files to validate")
    
    # Validate each pattern file
    validation_failed = False
    for pattern_file in pattern_files:
        if not validate_pattern_file(pattern_file):
            validation_failed = True
    
    if validation_failed:
        print("\nValidation failed!")
        return 1
    else:
        print("\nAll pattern files validated successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())