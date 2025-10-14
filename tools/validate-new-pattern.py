#!/usr/bin/env python3
"""
Validation script for the new pattern format (by-vendor structure)
"""

import json
import sys
import os
import re


def validate_new_pattern(file_path):
    """Validate a pattern file in the new format"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check required top-level fields
        required_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category']
        for field in required_fields:
            if field not in data:
                print(f"Error: Missing required field '{field}'")
                return False
        
        # Check versions structure
        if 'versions' in data:
            if not isinstance(data['versions'], dict):
                print("Error: 'versions' must be an object")
                return False
            
            for version, patterns in data['versions'].items():
                if not isinstance(patterns, list):
                    print(f"Error: 'versions.{version}' must be an array")
                    return False
                
                for pattern in patterns:
                    if not validate_pattern_structure(pattern):
                        return False
        
        # Check all_versions structure
        if 'all_versions' in data:
            if not isinstance(data['all_versions'], list):
                print("Error: 'all_versions' must be an array")
                return False
            
            for pattern in data['all_versions']:
                if not validate_pattern_structure(pattern):
                    return False
        
        print(f"Valid pattern file: {file_path}")
        return True
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error validating {file_path}: {e}")
        return False


def validate_pattern_structure(pattern):
    """Validate the structure of a single pattern"""
    # Check required fields
    required_fields = ['name', 'pattern', 'version_group', 'priority', 'confidence']
    for field in required_fields:
        if field not in pattern:
            print(f"Error: Missing required field '{field}' in pattern")
            return False
    
    # Validate pattern is a valid regex
    try:
        re.compile(pattern['pattern'])
    except re.error as e:
        print(f"Error: Invalid regex pattern '{pattern['pattern']}': {e}")
        return False
    
    # Validate version_group is an integer
    if not isinstance(pattern['version_group'], int):
        print(f"Error: version_group must be an integer")
        return False
    
    # Validate priority is between 0 and 200
    if not isinstance(pattern['priority'], int) or pattern['priority'] < 0 or pattern['priority'] > 200:
        print(f"Error: priority must be an integer between 0 and 200")
        return False
    
    # Validate confidence is between 0.0 and 1.0
    if not isinstance(pattern['confidence'], (int, float)) or pattern['confidence'] < 0.0 or pattern['confidence'] > 1.0:
        print(f"Error: confidence must be a number between 0.0 and 1.0")
        return False
    
    # Validate metadata if present
    if 'metadata' in pattern:
        if not isinstance(pattern['metadata'], dict):
            print(f"Error: metadata must be an object")
            return False
        
        # Check required metadata fields
        required_metadata_fields = ['author', 'created_at', 'updated_at', 'description', 'tags']
        for field in required_metadata_fields:
            if field not in pattern['metadata']:
                print(f"Error: Missing required metadata field '{field}'")
                return False
        
        # Validate tags is an array
        if not isinstance(pattern['metadata']['tags'], list):
            print(f"Error: metadata.tags must be an array")
            return False
        
        # Validate test_cases if present
        if 'test_cases' in pattern['metadata']:
            if not isinstance(pattern['metadata']['test_cases'], list):
                print(f"Error: metadata.test_cases must be an array")
                return False
            
            for test_case in pattern['metadata']['test_cases']:
                if not isinstance(test_case, dict):
                    print(f"Error: Each test case must be an object")
                    return False
                
                if 'input' not in test_case or 'expected_version' not in test_case:
                    print(f"Error: Test cases must have 'input' and 'expected_version' fields")
                    return False
    
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate-new-pattern.py <pattern-file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    if validate_new_pattern(file_path):
        sys.exit(0)
    else:
        sys.exit(1)