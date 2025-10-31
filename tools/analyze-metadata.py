#!/usr/bin/env python3
"""
Script to analyze metadata completeness in pattern files
"""

import json
import os
import sys
from collections import defaultdict


def analyze_pattern_metadata(file_path):
    """Analyze metadata completeness in a pattern file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Track missing metadata fields
        missing_fields = {
            'required': [],
            'optional': []
        }
        
        # Check top-level fields
        required_top_fields = ['vendor', 'vendor_id', 'product', 'product_id', 'category', 'subcategory']
        for field in required_top_fields:
            if field not in data:
                missing_fields['required'].append(f"top-level.{field}")
        
        # Check patterns for metadata
        all_patterns = []
        if 'all_versions' in data:
            all_patterns.extend(data['all_versions'])
        if 'versions' in data:
            for version_patterns in data['versions'].values():
                all_patterns.extend(version_patterns)
        
        pattern_metadata_stats = {
            'total_patterns': len(all_patterns),
            'patterns_with_metadata': 0,
            'missing_required_metadata': 0,
            'missing_optional_metadata': 0
        }
        
        required_metadata_fields = ['author', 'created_at', 'updated_at', 'description', 'tags']
        optional_metadata_fields = ['references', 'severity', 'cvss_score', 'cwe_ids', 
                                  'affected_versions', 'remediation', 'source', 'license', 'test_cases']
        
        for pattern in all_patterns:
            if 'metadata' in pattern:
                pattern_metadata_stats['patterns_with_metadata'] += 1
                metadata = pattern['metadata']
                
                # Check required metadata fields
                for field in required_metadata_fields:
                    if field not in metadata:
                        missing_fields['required'].append(f"pattern.metadata.{field}")
                
                # Check optional metadata fields
                for field in optional_metadata_fields:
                    if field not in metadata:
                        missing_fields['optional'].append(f"pattern.metadata.{field}")
            else:
                pattern_metadata_stats['missing_required_metadata'] += len(required_metadata_fields)
                pattern_metadata_stats['missing_optional_metadata'] += len(optional_metadata_fields)
        
        return missing_fields, pattern_metadata_stats
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None, None


def analyze_all_patterns(patterns_dir):
    """Analyze metadata completeness in all pattern files."""
    total_files = 0
    files_with_issues = 0
    
    # Track overall statistics
    overall_missing_required = defaultdict(int)
    overall_missing_optional = defaultdict(int)
    overall_pattern_stats = {
        'total_patterns': 0,
        'patterns_with_metadata': 0,
        'missing_required_metadata': 0,
        'missing_optional_metadata': 0
    }
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                total_files += 1
                
                missing_fields, pattern_stats = analyze_pattern_metadata(file_path)
                if missing_fields is not None:
                    # Update overall statistics
                    for field in missing_fields['required']:
                        overall_missing_required[field] += 1
                    
                    for field in missing_fields['optional']:
                        overall_missing_optional[field] += 1
                    
                    if pattern_stats:
                        for key in overall_pattern_stats:
                            overall_pattern_stats[key] += pattern_stats.get(key, 0)
                    
                    # Count files with issues
                    if missing_fields['required'] or missing_fields['optional']:
                        files_with_issues += 1
                        
                        # Print detailed info for files with many missing fields
                        if len(missing_fields['required']) > 5 or len(missing_fields['optional']) > 10:
                            print(f"\nFile with many missing fields: {file_path}")
                            if missing_fields['required']:
                                print(f"  Missing required fields: {missing_fields['required']}")
                            if missing_fields['optional']:
                                print(f"  Missing optional fields: {missing_fields['optional']}")
    
    # Print summary
    print(f"\n=== Metadata Analysis Summary ===")
    print(f"Total files analyzed: {total_files}")
    print(f"Files with missing metadata: {files_with_issues}")
    print(f"Files with complete metadata: {total_files - files_with_issues}")
    
    print(f"\nPattern Statistics:")
    print(f"  Total patterns: {overall_pattern_stats['total_patterns']}")
    print(f"  Patterns with metadata: {overall_pattern_stats['patterns_with_metadata']}")
    print(f"  Patterns missing metadata: {overall_pattern_stats['total_patterns'] - overall_pattern_stats['patterns_with_metadata']}")
    
    if overall_missing_required:
        print(f"\nMost commonly missing required fields:")
        sorted_required = sorted(overall_missing_required.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_required[:10]:
            print(f"  {field}: {count} files")
    
    if overall_missing_optional:
        print(f"\nMost commonly missing optional fields:")
        sorted_optional = sorted(overall_missing_optional.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_optional[:10]:
            print(f"  {field}: {count} files")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        patterns_dir = sys.argv[1]
    else:
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
    
    if not os.path.exists(patterns_dir):
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)
    
    analyze_all_patterns(patterns_dir)