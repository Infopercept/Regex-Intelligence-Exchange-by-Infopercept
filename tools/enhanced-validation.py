#!/usr/bin/env python3
"""
Enhanced validation script with detailed reporting and statistics
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


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


def analyze_pattern_quality(data, file_path):
    """Analyze the quality of a pattern file."""
    quality_metrics = {
        'has_subcategory': 'subcategory' in data,
        'has_versions': 'versions' in data and bool(data['versions']),
        'has_all_versions': 'all_versions' in data and bool(data['all_versions']),
        'pattern_count': 0,
        'patterns_with_metadata': 0,
        'patterns_with_test_cases': 0,
        'patterns_with_references': 0,
        'patterns_with_severity': 0,
        'patterns_with_cvss': 0,
        'total_test_cases': 0,
        'category': data.get('category', 'unknown'),
        'subcategory': data.get('subcategory', 'unknown')
    }
    
    # Analyze all_versions patterns
    all_versions = data.get('all_versions', []) if isinstance(data, dict) else []
    quality_metrics['pattern_count'] += len(all_versions)
    
    for pattern in all_versions:
        if 'metadata' in pattern:
            quality_metrics['patterns_with_metadata'] += 1
            metadata = pattern['metadata']
            
            if 'test_cases' in metadata:
                quality_metrics['patterns_with_test_cases'] += 1
                quality_metrics['total_test_cases'] += len(metadata['test_cases'])
            
            if 'references' in metadata:
                quality_metrics['patterns_with_references'] += 1
            
            if 'severity' in metadata:
                quality_metrics['patterns_with_severity'] += 1
            
            if 'cvss_score' in metadata:
                quality_metrics['patterns_with_cvss'] += 1
    
    # Analyze version-specific patterns
    versions = data.get('versions', {}) if isinstance(data, dict) else {}
    for version_patterns in versions.values():
        quality_metrics['pattern_count'] += len(version_patterns)
        
        for pattern in version_patterns:
            if 'metadata' in pattern:
                quality_metrics['patterns_with_metadata'] += 1
                metadata = pattern['metadata']
                
                if 'test_cases' in metadata:
                    quality_metrics['patterns_with_test_cases'] += 1
                    quality_metrics['total_test_cases'] += len(metadata['test_cases'])
                
                if 'references' in metadata:
                    quality_metrics['patterns_with_references'] += 1
                
                if 'severity' in metadata:
                    quality_metrics['patterns_with_severity'] += 1
                
                if 'cvss_score' in metadata:
                    quality_metrics['patterns_with_cvss'] += 1
    
    return quality_metrics


def validate_pattern_file(file_path):
    """Validate a pattern file with detailed analysis."""
    print(f"Validating {file_path}...")
    
    # Validate JSON structure
    json_valid, data, json_msg = validate_json_structure(file_path)
    if not json_valid:
        return False, json_msg, None
    
    # Validate required fields
    fields_valid, fields_msg = validate_required_fields(data, file_path)
    if not fields_valid:
        return False, fields_msg, None
    
    # Test all_versions patterns
    all_versions_tests = []
    all_versions = data.get('all_versions', []) if isinstance(data, dict) else []
    for i, pattern in enumerate(all_versions):
        # Validate structure
        struct_valid, struct_msg = validate_pattern_structure(pattern, file_path, f"all_versions[{i}]")
        if not struct_valid:
            return False, struct_msg, None
        all_versions_tests.append((struct_valid, struct_msg))
    
    # Test version-specific patterns
    versions_tests = []
    versions = data.get('versions', {}) if isinstance(data, dict) else {}
    for version_range, version_patterns in versions.items():
        for i, pattern in enumerate(version_patterns):
            # Validate structure
            struct_valid, struct_msg = validate_pattern_structure(pattern, file_path, f"versions.{version_range}[{i}]")
            if not struct_valid:
                return False, struct_msg, None
            versions_tests.append((struct_valid, struct_msg))
    
    # Analyze pattern quality
    quality_metrics = analyze_pattern_quality(data, file_path)
    
    return True, "Pattern file validated successfully", quality_metrics


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
        
        valid, msg, quality_metrics = validate_pattern_file(file_path)
        if valid:
            print(f"✓ {msg}")
            if quality_metrics:
                print(f"Pattern Quality Metrics:")
                print(f"  - Has subcategory: {quality_metrics['has_subcategory']}")
                print(f"  - Has version-specific patterns: {quality_metrics['has_versions']}")
                print(f"  - Has all-versions patterns: {quality_metrics['has_all_versions']}")
                print(f"  - Total patterns: {quality_metrics['pattern_count']}")
                print(f"  - Patterns with metadata: {quality_metrics['patterns_with_metadata']}")
                print(f"  - Patterns with test cases: {quality_metrics['patterns_with_test_cases']}")
                print(f"  - Patterns with references: {quality_metrics['patterns_with_references']}")
                print(f"  - Patterns with severity: {quality_metrics['patterns_with_severity']}")
                print(f"  - Patterns with CVSS score: {quality_metrics['patterns_with_cvss']}")
                print(f"  - Total test cases: {quality_metrics['total_test_cases']}")
            return 0
        else:
            print(f"✗ {msg}")
            return 1
    else:
        print("Running comprehensive validation on all pattern files...")
        
        # Find all pattern files
        pattern_files = find_pattern_files(repo_root)
        
        if not pattern_files:
            print("No pattern files found!")
            return 1
        
        print(f"Found {len(pattern_files)} pattern files to validate")
        
        # Validate each pattern file
        validation_passed = 0
        validation_failed = 0
        quality_stats = defaultdict(int)
        category_stats = defaultdict(int)
        subcategory_stats = defaultdict(int)
        
        for pattern_file in pattern_files:
            try:
                valid, msg, quality_metrics = validate_pattern_file(pattern_file)
                if valid:
                    print(f"✓ {os.path.basename(pattern_file)}: {msg}")
                    validation_passed += 1
                    
                    # Update quality statistics
                    if quality_metrics:
                        quality_stats['total_patterns'] += quality_metrics['pattern_count']
                        quality_stats['patterns_with_metadata'] += quality_metrics['patterns_with_metadata']
                        quality_stats['patterns_with_test_cases'] += quality_metrics['patterns_with_test_cases']
                        quality_stats['patterns_with_references'] += quality_metrics['patterns_with_references']
                        quality_stats['patterns_with_severity'] += quality_metrics['patterns_with_severity']
                        quality_stats['patterns_with_cvss'] += quality_metrics['patterns_with_cvss']
                        quality_stats['total_test_cases'] += quality_metrics['total_test_cases']
                        
                        if quality_metrics['has_subcategory']:
                            quality_stats['files_with_subcategory'] += 1
                        
                        if quality_metrics['has_versions']:
                            quality_stats['files_with_versions'] += 1
                        
                        if quality_metrics['has_all_versions']:
                            quality_stats['files_with_all_versions'] += 1
                        
                        # Update category statistics
                        category_stats[quality_metrics['category']] += 1
                        
                        # Update subcategory statistics
                        subcategory_stats[quality_metrics['subcategory']] += 1
                else:
                    print(f"✗ {os.path.basename(pattern_file)}: {msg}")
                    validation_failed += 1
            except Exception as e:
                print(f"✗ {os.path.basename(pattern_file)}: Unexpected error - {e}")
                validation_failed += 1
        
        print(f"\nValidation Results: {validation_passed} passed, {validation_failed} failed")
        
        # Print quality statistics
        if quality_stats:
            print(f"\nQuality Statistics:")
            print(f"  - Files with subcategory: {quality_stats['files_with_subcategory']}/{len(pattern_files)} ({quality_stats['files_with_subcategory']/len(pattern_files)*100:.1f}%)")
            print(f"  - Files with version-specific patterns: {quality_stats['files_with_versions']}/{len(pattern_files)} ({quality_stats['files_with_versions']/len(pattern_files)*100:.1f}%)")
            print(f"  - Files with all-versions patterns: {quality_stats['files_with_all_versions']}/{len(pattern_files)} ({quality_stats['files_with_all_versions']/len(pattern_files)*100:.1f}%)")
            print(f"  - Total patterns: {quality_stats['total_patterns']}")
            print(f"  - Patterns with metadata: {quality_stats['patterns_with_metadata']}/{quality_stats['total_patterns']} ({quality_stats['patterns_with_metadata']/quality_stats['total_patterns']*100:.1f}%)")
            print(f"  - Patterns with test cases: {quality_stats['patterns_with_test_cases']}/{quality_stats['total_patterns']} ({quality_stats['patterns_with_test_cases']/quality_stats['total_patterns']*100:.1f}%)")
            print(f"  - Patterns with references: {quality_stats['patterns_with_references']}/{quality_stats['total_patterns']} ({quality_stats['patterns_with_references']/quality_stats['total_patterns']*100:.1f}%)")
            print(f"  - Patterns with severity: {quality_stats['patterns_with_severity']}/{quality_stats['total_patterns']} ({quality_stats['patterns_with_severity']/quality_stats['total_patterns']*100:.1f}%)")
            print(f"  - Patterns with CVSS score: {quality_stats['patterns_with_cvss']}/{quality_stats['total_patterns']} ({quality_stats['patterns_with_cvss']/quality_stats['total_patterns']*100:.1f}%)")
            print(f"  - Total test cases: {quality_stats['total_test_cases']}")
        
        # Print category statistics
        if category_stats:
            print(f"\nCategory Distribution:")
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {category}: {count} files ({count/len(pattern_files)*100:.1f}%)")
        
        if validation_failed > 0:
            return 1
        else:
            return 0


if __name__ == "__main__":
    sys.exit(main())