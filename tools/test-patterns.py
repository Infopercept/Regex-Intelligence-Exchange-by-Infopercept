#!/usr/bin/env python3
"""
Comprehensive test runner for pattern validation and testing
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Import version utilities
sys.path.append(os.path.dirname(__file__))
import version_utils


def find_pattern_files(root_dir):
    """Find all pattern files in the repository."""
    pattern_files = []
    patterns_dir = os.path.join(root_dir, 'patterns')
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                pattern_files.append(os.path.join(root, file))
    
    return pattern_files


def validate_json_structure(file_path):
    """Validate JSON structure of a pattern file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {e}"
    except Exception as e:
        return False, None, f"Error reading file: {e}"


def validate_required_fields(data, file_path):
    """Validate required top-level fields."""
    if not isinstance(data, dict):
        return False, "Data must be a JSON object"
        
    required_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return False, f"Missing required fields: {missing_fields}"
    
    # Validate category
    allowed_categories = ['web', 'cms', 'database', 'framework', 'messaging', 'networking', 'os']
    if data['category'] not in allowed_categories:
        return False, f"Invalid category '{data['category']}'. Must be one of {allowed_categories}"
    
    return True, "Required fields validation passed"


def validate_pattern_structure(pattern, file_path, pattern_index=None):
    """Validate the structure of a single pattern."""
    pattern_id = f"Pattern {pattern_index}" if pattern_index is not None else "Pattern"
    
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
        metadata_result, metadata_msg = validate_metadata(pattern['metadata'], pattern_id)
        if not metadata_result:
            return False, metadata_msg
    
    return True, f"{pattern_id}: Structure validation passed"


def validate_metadata(metadata, pattern_id):
    """Validate pattern metadata."""
    # Check required metadata fields
    required_metadata_fields = ['author', 'created_at', 'updated_at', 'description', 'tags']
    missing_fields = [field for field in required_metadata_fields if field not in metadata]
    
    if missing_fields:
        return False, f"{pattern_id}: Missing required metadata fields: {missing_fields}"
    
    # Validate tags is an array
    if not isinstance(metadata['tags'], list):
        return False, f"{pattern_id}: metadata.tags must be an array"
    
    # Validate date formats
    date_fields = ['created_at', 'updated_at']
    for field in date_fields:
        try:
            datetime.strptime(metadata[field], '%Y-%m-%d')
        except ValueError:
            try:
                datetime.strptime(metadata[field], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return False, f"{pattern_id}: {field} must be in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format"
    
    # Validate optional metadata fields if present
    optional_fields = {
        'references': list,
        'severity': str,
        'cvss_score': (int, float),
        'cwe_ids': list,
        'affected_versions': list,
        'remediation': str,
        'source': str,
        'license': str
    }
    
    for field, expected_type in optional_fields.items():
        if field in metadata:
            if not isinstance(metadata[field], expected_type):
                return False, f"{pattern_id}: metadata.{field} must be of type {expected_type}"
    
    # Validate severity if present
    if 'severity' in metadata:
        allowed_severities = ['low', 'medium', 'high', 'critical']
        if metadata['severity'] not in allowed_severities:
            return False, f"{pattern_id}: metadata.severity must be one of {allowed_severities}"
    
    # Validate CVSS score if present
    if 'cvss_score' in metadata:
        score = metadata['cvss_score']
        if not isinstance(score, (int, float)) or score < 0.0 or score > 10.0:
            return False, f"{pattern_id}: metadata.cvss_score must be a number between 0.0 and 10.0"
    
    # Validate references if present
    if 'references' in metadata:
        if not isinstance(metadata['references'], list):
            return False, f"{pattern_id}: metadata.references must be an array"
        
        for i, ref in enumerate(metadata['references']):
            if not isinstance(ref, dict):
                return False, f"{pattern_id}: Reference {i} must be an object"
            
            if 'title' not in ref or 'url' not in ref:
                return False, f"{pattern_id}: Reference {i} must have 'title' and 'url' fields"
    
    # Validate test_cases if present
    if 'test_cases' in metadata:
        if not isinstance(metadata['test_cases'], list):
            return False, f"{pattern_id}: metadata.test_cases must be an array"
        
        for i, test_case in enumerate(metadata['test_cases']):
            if not isinstance(test_case, dict):
                return False, f"{pattern_id}: Test case {i} must be an object"
            
            if 'input' not in test_case or 'expected_version' not in test_case:
                return False, f"{pattern_id}: Test case {i} must have 'input' and 'expected_version' fields"
    
    return True, f"{pattern_id}: Metadata validation passed"


def run_test_cases(pattern, file_path):
    """Run test cases for a pattern with enhanced version extraction."""
    if 'metadata' not in pattern or 'test_cases' not in pattern['metadata']:
        return True, "No test cases to run"
    
    test_cases = pattern['metadata']['test_cases']
    passed_tests = 0
    failed_tests = 0
    
    try:
        regex = re.compile(pattern['pattern'])
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"
    
    for i, test_case in enumerate(test_cases):
        try:
            input_text = test_case['input']
            expected_version = test_case['expected_version']
            
            match = regex.search(input_text)
            if match:
                # Extract version using enhanced version extraction
                if pattern['version_group'] > 0 and pattern['version_group'] <= len(match.groups()):
                    raw_version = match.group(pattern['version_group'])
                    actual_version = version_utils.normalize_version(raw_version)
                else:
                    # If no version group or invalid group, use the full match
                    actual_version = match.group(0)
                    # Try to normalize if it looks like a version
                    if re.search(r'\d', actual_version):
                        normalized = version_utils.normalize_version(actual_version)
                        if normalized:
                            actual_version = normalized
                
                # Compare versions using enhanced comparison
                if expected_version == "unknown":
                    # For "unknown" expected version, any match is considered a pass
                    passed_tests += 1
                elif actual_version is None and expected_version is None:
                    # Both are None, consider it a pass
                    passed_tests += 1
                elif actual_version is not None and expected_version is not None:
                    # Both are not None, compare them
                    if actual_version == expected_version:
                        passed_tests += 1
                    else:
                        # Try normalized comparison
                        normalized_actual = version_utils.normalize_version(actual_version)
                        normalized_expected = version_utils.normalize_version(expected_version)
                        if normalized_actual == normalized_expected:
                            passed_tests += 1
                        else:
                            failed_tests += 1
                            print(f"  Test case {i+1} failed: expected '{expected_version}' (normalized: {normalized_expected}), got '{actual_version}' (normalized: {normalized_actual})")
                else:
                    # One is None and the other is not
                    failed_tests += 1
                    print(f"  Test case {i+1} failed: expected '{expected_version}', got '{actual_version}'")
            else:
                if expected_version == "unknown" or expected_version is None:
                    passed_tests += 1
                else:
                    failed_tests += 1
                    print(f"  Test case {i+1} failed: no match found, expected '{expected_version}'")
        except Exception as e:
            failed_tests += 1
            print(f"  Test case {i+1} error: {e}")
    
    if failed_tests == 0:
        return True, f"All {passed_tests} test cases passed"
    else:
        return False, f"{passed_tests}/{len(test_cases)} test cases passed, {failed_tests} failed"


def test_pattern_file(file_path):
    """Run comprehensive tests on a pattern file."""
    print(f"Testing {file_path}...")
    
    # Validate JSON structure
    json_valid, data, json_msg = validate_json_structure(file_path)
    if not json_valid:
        return False, json_msg
    
    # Validate required fields
    fields_valid, fields_msg = validate_required_fields(data, file_path)
    if not fields_valid:
        return False, fields_msg
    
    # Test all_versions patterns
    all_versions_tests = []
    all_versions = data.get('all_versions', []) if isinstance(data, dict) else []
    for i, pattern in enumerate(all_versions):
        # Validate structure
        struct_valid, struct_msg = validate_pattern_structure(pattern, file_path, f"all_versions[{i}]")
        if not struct_valid:
            return False, struct_msg
        
        # Run test cases
        test_valid, test_msg = run_test_cases(pattern, file_path)
        all_versions_tests.append((test_valid, test_msg))
    
    # Test version-specific patterns
    versions_tests = []
    versions = data.get('versions', {}) if isinstance(data, dict) else {}
    for version_range, version_patterns in versions.items():
        for i, pattern in enumerate(version_patterns):
            # Validate structure
            struct_valid, struct_msg = validate_pattern_structure(pattern, file_path, f"versions.{version_range}[{i}]")
            if not struct_valid:
                return False, struct_msg
            
            # Run test cases
            test_valid, test_msg = run_test_cases(pattern, file_path)
            versions_tests.append((test_valid, test_msg))
    
    # Check if any tests failed
    failed_tests = [msg for valid, msg in all_versions_tests + versions_tests if not valid]
    if failed_tests:
        return False, f"Some test cases failed: {', '.join(failed_tests)}"
    
    return True, "All tests passed"


def main():
    """Main function."""
    # Get the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    # Check if a specific file was provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return 1
        
        valid, msg = test_pattern_file(file_path)
        if valid:
            print(f"✓ {msg}")
            return 0
        else:
            print(f"✗ {msg}")
            return 1
    else:
        print("Running comprehensive tests on all pattern files...")
        
        # Find all pattern files
        pattern_files = find_pattern_files(repo_root)
        
        if not pattern_files:
            print("No pattern files found!")
            return 1
        
        print(f"Found {len(pattern_files)} pattern files to test")
        
        # Test each pattern file
        passed_files = 0
        failed_files = 0
        
        for pattern_file in pattern_files:
            try:
                valid, msg = test_pattern_file(pattern_file)
                if valid:
                    print(f"✓ {os.path.basename(pattern_file)}: {msg}")
                    passed_files += 1
                else:
                    print(f"✗ {os.path.basename(pattern_file)}: {msg}")
                    failed_files += 1
            except Exception as e:
                print(f"✗ {os.path.basename(pattern_file)}: Unexpected error - {e}")
                failed_files += 1
        
        print(f"\nTest Results: {passed_files} passed, {failed_files} failed")
        
        if failed_files > 0:
            return 1
        else:
            return 0


if __name__ == "__main__":
    sys.exit(main())