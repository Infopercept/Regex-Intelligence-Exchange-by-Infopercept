#!/usr/bin/env python3
"""
Script to validate and test WebTech imported patterns
"""

import json
import os
import re
import sys
from pathlib import Path


def find_webtech_pattern_files(root_dir):
    """Find all WebTech imported pattern files."""
    pattern_files = []
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                pattern_files.append(os.path.join(root, file))
    
    return pattern_files


def validate_webtech_pattern(file_path):
    """
    Validate a WebTech imported pattern file.
    
    Args:
        file_path (str): Path to the pattern file
        
    Returns:
        tuple: (is_valid, message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required top-level fields
        required_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category', 'subcategory']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"
        
        # Check all_versions patterns
        all_versions = data.get('all_versions', [])
        for i, pattern in enumerate(all_versions):
            valid, msg = validate_pattern_structure(pattern, f"all_versions[{i}]")
            if not valid:
                return False, msg
        
        # Check version-specific patterns
        versions = data.get('versions', {})
        for version_range, version_patterns in versions.items():
            for i, pattern in enumerate(version_patterns):
                valid, msg = validate_pattern_structure(pattern, f"versions.{version_range}[{i}]")
                if not valid:
                    return False, msg
        
        return True, "Pattern validation passed"
    except Exception as e:
        return False, f"Error processing file: {e}"


def validate_pattern_structure(pattern, pattern_id):
    """
    Validate the structure of a single pattern.
    
    Args:
        pattern (dict): Pattern data
        pattern_id (str): Pattern identifier for reporting
        
    Returns:
        tuple: (is_valid, message)
    """
    # Check required fields
    required_fields = ['name', 'pattern', 'version_group', 'priority', 'confidence']
    missing_fields = [field for field in required_fields if field not in pattern]
    
    if missing_fields:
        return False, f"{pattern_id}: Missing required fields: {missing_fields}"
    
    # Validate pattern is a valid regex
    try:
        re.compile(pattern['pattern'])
    except re.error as e:
        return False, f"{pattern_id}: Invalid regex pattern '{pattern['pattern']}': {e}"
    
    # Validate version_group is an integer
    if not isinstance(pattern['version_group'], int):
        return False, f"{pattern_id}: version_group must be an integer"
    
    # Validate priority is between 0 and 200
    if not isinstance(pattern['priority'], int) or pattern['priority'] < 0 or pattern['priority'] > 200:
        return False, f"{pattern_id}: priority must be an integer between 0 and 200"
    
    # Validate confidence is between 0.0 and 1.0
    if not isinstance(pattern['confidence'], (int, float)) or pattern['confidence'] < 0.0 or pattern['confidence'] > 1.0:
        return False, f"{pattern_id}: confidence must be a number between 0.0 and 1.0"
    
    # Validate metadata if present
    if 'metadata' in pattern:
        valid, msg = validate_metadata(pattern['metadata'], pattern_id)
        if not valid:
            return False, msg
    
    return True, f"{pattern_id}: Structure validation passed"


def validate_metadata(metadata, pattern_id):
    """
    Validate pattern metadata.
    
    Args:
        metadata (dict): Metadata dictionary
        pattern_id (str): Pattern identifier for reporting
        
    Returns:
        tuple: (is_valid, message)
    """
    # Check required metadata fields
    required_metadata_fields = ['author', 'created_at', 'updated_at', 'description', 'tags']
    missing_fields = [field for field in required_metadata_fields if field not in metadata]
    
    if missing_fields:
        return False, f"{pattern_id}: Missing required metadata fields: {missing_fields}"
    
    # Validate tags is an array
    if not isinstance(metadata['tags'], list):
        return False, f"{pattern_id}: metadata.tags must be an array"
    
    # Validate date formats
    import datetime
    date_fields = ['created_at', 'updated_at']
    for field in date_fields:
        try:
            datetime.datetime.strptime(metadata[field], '%Y-%m-%d')
        except ValueError:
            try:
                datetime.datetime.strptime(metadata[field], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return False, f"{pattern_id}: {field} must be in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format"
    
    return True, f"{pattern_id}: Metadata validation passed"


def main():
    """Main function."""
    # Get the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    webtech_patterns_dir = os.path.join(repo_root, 'imported-webtech-patterns')
    
    # Check if WebTech patterns directory exists
    if not os.path.exists(webtech_patterns_dir):
        print("WebTech patterns directory not found!")
        return 1
    
    print("Validating WebTech imported patterns...")
    
    # Find all WebTech imported pattern files
    pattern_files = find_webtech_pattern_files(webtech_patterns_dir)
    
    if not pattern_files:
        print("No WebTech imported pattern files found!")
        return 1
    
    print(f"Found {len(pattern_files)} WebTech imported pattern files to validate")
    
    # Validate each pattern file
    passed_files = 0
    failed_files = 0
    failed_files_list = []
    
    for pattern_file in pattern_files:
        try:
            valid, msg = validate_webtech_pattern(pattern_file)
            # Clean the filename for display to avoid encoding issues
            clean_filename = os.path.basename(pattern_file)
            if valid:
                print(f"PASS {clean_filename}: {msg}")
                passed_files += 1
            else:
                print(f"FAIL {clean_filename}: {msg}")
                failed_files += 1
                failed_files_list.append(clean_filename)
        except Exception as e:
            clean_filename = os.path.basename(pattern_file)
            print(f"ERROR {clean_filename}: Unexpected error - {e}")
            failed_files += 1
            failed_files_list.append(clean_filename)
    
    print(f"\nValidation Results: {passed_files} passed, {failed_files} failed")
    
    if failed_files_list:
        print("\nFailed files:")
        for failed_file in failed_files_list:
            print(f"  - {failed_file}")
    
    if failed_files > 0:
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())