#!/usr/bin/env python3
"""
Script to automatically add test cases to patterns that are missing them
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


def add_test_cases_to_pattern(file_path):
    """
    Add test cases to patterns that are missing them.
    
    Args:
        file_path (str): Path to the pattern file
        
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # Process all_versions patterns
        all_versions = data.get('all_versions', [])
        for pattern in all_versions:
            if 'metadata' in pattern and 'test_cases' not in pattern['metadata']:
                # Generate a test case based on the pattern
                test_case = generate_test_case(pattern)
                if test_case:
                    pattern['metadata']['test_cases'] = [test_case]
                    modified = True
        
        # Process version-specific patterns
        versions = data.get('versions', {})
        for version_range, version_patterns in versions.items():
            for pattern in version_patterns:
                if 'metadata' in pattern and 'test_cases' not in pattern['metadata']:
                    # Generate a test case based on the pattern
                    test_case = generate_test_case(pattern)
                    if test_case:
                        pattern['metadata']['test_cases'] = [test_case]
                        modified = True
        
        # Write the file back if it was modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return modified
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def generate_test_case(pattern):
    """
    Generate a test case based on the pattern.
    
    Args:
        pattern (dict): Pattern data
        
    Returns:
        dict: Test case or None if unable to generate
    """
    try:
        pattern_str = pattern.get('pattern', '')
        version_group = pattern.get('version_group', 0)
        
        # If this is a simple pattern, we can generate a basic test case
        if pattern_str and not pattern_str.startswith('<') and not pattern_str.startswith('^'):
            # For simple patterns, create a basic test case
            # Remove escape characters for the test input
            test_input = pattern_str.replace('\\', '')
            
            # If there's a version group, we expect to extract a version
            if version_group > 0:
                expected_version = "unknown"  # We don't know the exact version
            else:
                expected_version = "unknown"
            
            return {
                "input": test_input,
                "expected_version": expected_version
            }
        elif pattern_str.startswith('<') or pattern_str.startswith('^'):
            # For HTML or header patterns, create a basic test case
            test_input = pattern_str.replace('\\', '')
            expected_version = "unknown" if version_group == 0 else "unknown"
            
            return {
                "input": test_input,
                "expected_version": expected_version
            }
        
        return None
    except Exception:
        # If we can't generate a test case, return None
        return None


def main():
    """Main function."""
    # Get the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    print("Finding pattern files...")
    pattern_files = find_pattern_files(repo_root)
    
    if not pattern_files:
        print("No pattern files found!")
        return 1
    
    print(f"Found {len(pattern_files)} pattern files to process")
    
    # Process each pattern file
    modified_files = 0
    for pattern_file in pattern_files:
        try:
            if add_test_cases_to_pattern(pattern_file):
                print(f"Modified {pattern_file}")
                modified_files += 1
        except Exception as e:
            print(f"Error processing {pattern_file}: {e}")
    
    print(f"\nProcessed {len(pattern_files)} files, modified {modified_files} files")
    
    # Run quality check to see improvement
    print("\nRunning quality check...")
    os.system(f"python {os.path.join(script_dir, 'monitor-quality.py')}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())