#!/usr/bin/env python3
"""
Script to optimize pattern files for better performance
"""

import json
import os
import sys
import re
from pathlib import Path


def precompile_patterns(file_path):
    """Precompile regex patterns in a pattern file for better performance."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Precompile patterns and add compiled regex to metadata
        modified = False
        
        # Process all_versions patterns
        if 'all_versions' in data:
            for pattern in data['all_versions']:
                if 'pattern' in pattern:
                    try:
                        # Precompile the regex pattern
                        compiled = re.compile(pattern['pattern'])
                        # Add a note that this pattern has been precompiled
                        if 'metadata' not in pattern:
                            pattern['metadata'] = {}
                        pattern['metadata']['compiled_pattern'] = True
                        modified = True
                    except re.error as e:
                        print(f"Warning: Invalid regex in {file_path}: {e}")
        
        # Process version-specific patterns
        if 'versions' in data:
            for version, version_patterns in data['versions'].items():
                for pattern in version_patterns:
                    if 'pattern' in pattern:
                        try:
                            # Precompile the regex pattern
                            compiled = re.compile(pattern['pattern'])
                            # Add a note that this pattern has been precompiled
                            if 'metadata' not in pattern:
                                pattern['metadata'] = {}
                            pattern['metadata']['compiled_pattern'] = True
                            modified = True
                        except re.error as e:
                            print(f"Warning: Invalid regex in {file_path}: {e}")
        
        # Write the optimized data back to the file if modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Optimized {file_path}")
            return True
        else:
            print(f"No optimization needed for {file_path}")
            return False
    
    except Exception as e:
        print(f"Error optimizing {file_path}: {e}")
        return False


def optimize_all_patterns(patterns_dir, limit=None):
    """Optimize all pattern files for better performance."""
    optimized_files = 0
    error_files = 0
    processed_files = 0
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                processed_files += 1
                
                if precompile_patterns(file_path):
                    optimized_files += 1
                
                # Limit processing if specified
                if limit and processed_files >= limit:
                    break
        
        if limit and processed_files >= limit:
            break
    
    print(f"\nSummary: {optimized_files} files optimized, {error_files} errors, {processed_files} processed")


def create_performance_cache(patterns_dir):
    """Create a performance cache for faster pattern loading."""
    cache = {}
    cache_file = os.path.join(patterns_dir, '..', '..', 'data', 'pattern_cache.json')
    
    print("Creating performance cache...")
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, patterns_dir)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract key information for fast lookup
                    cache_entry = {
                        'vendor': data.get('vendor', ''),
                        'product': data.get('product', ''),
                        'category': data.get('category', ''),
                        'subcategory': data.get('subcategory', ''),
                        'pattern_count': 0
                    }
                    
                    # Count patterns
                    if 'all_versions' in data:
                        cache_entry['pattern_count'] += len(data['all_versions'])
                    
                    if 'versions' in data:
                        for version_patterns in data['versions'].values():
                            cache_entry['pattern_count'] += len(version_patterns)
                    
                    cache[relative_path] = cache_entry
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    # Write cache to file
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"Performance cache created at {cache_file}")
    except Exception as e:
        print(f"Error creating performance cache: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        patterns_dir = sys.argv[1]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    else:
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
        limit = None
    
    if not os.path.exists(patterns_dir):
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)
    
    print("Optimizing pattern files...")
    optimize_all_patterns(patterns_dir, limit)
    
    print("\nCreating performance cache...")
    create_performance_cache(patterns_dir)