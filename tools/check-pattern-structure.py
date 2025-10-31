#!/usr/bin/env python3
"""
Script to check for pattern structure inconsistencies
"""

import json
import os
import sys
from pathlib import Path


def check_pattern_structure(file_path):
    """Check a pattern file for structural inconsistencies"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        issues = []
        
        # Check if subcategory is at the end instead of with other top-level fields
        keys = list(data.keys())
        if 'subcategory' in keys and keys.index('subcategory') != keys.index('category') + 1:
            issues.append("subcategory field is not positioned correctly after category")
        
        # Check if individual patterns have category/subcategory fields (they shouldn't)
        if 'all_versions' in data:
            for i, pattern in enumerate(data['all_versions']):
                if 'category' in pattern:
                    issues.append(f"Pattern {i} in all_versions has category field (should only be at top level)")
                if 'subcategory' in pattern:
                    issues.append(f"Pattern {i} in all_versions has subcategory field (should only be at top level)")
                if 'vendor' in pattern:
                    issues.append(f"Pattern {i} in all_versions has vendor field (should only be at top level)")
                if 'product' in pattern:
                    issues.append(f"Pattern {i} in all_versions has product field (should only be at top level)")
        
        # Check versions section
        if 'versions' in data:
            for version, patterns in data['versions'].items():
                for i, pattern in enumerate(patterns):
                    if 'category' in pattern:
                        issues.append(f"Pattern {i} in versions.{version} has category field (should only be at top level)")
                    if 'subcategory' in pattern:
                        issues.append(f"Pattern {i} in versions.{version} has subcategory field (should only be at top level)")
                    if 'vendor' in pattern:
                        issues.append(f"Pattern {i} in versions.{version} has vendor field (should only be at top level)")
                    if 'product' in pattern:
                        issues.append(f"Pattern {i} in versions.{version} has product field (should only be at top level)")
        
        if issues:
            print(f"Issues in {file_path}:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"Valid structure: {file_path}")
            return True
    
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False


def check_all_patterns(patterns_dir):
    """Check all pattern files in a directory"""
    valid_count = 0
    invalid_count = 0
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                if check_pattern_structure(file_path):
                    valid_count += 1
                else:
                    invalid_count += 1
    
    print(f"\nSummary: {valid_count} valid, {invalid_count} invalid pattern files")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        patterns_dir = sys.argv[1]
    else:
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
    
    if not os.path.exists(patterns_dir):
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)
    
    check_all_patterns(patterns_dir)