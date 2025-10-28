#!/usr/bin/env python3
"""
Script to merge patterns from different sources, handling duplicates intelligently
"""

import json
import os
import shutil
from datetime import datetime


def merge_metadata(existing_metadata, new_metadata):
    """
    Merge metadata from two sources, preferring newer or more complete data.
    
    Args:
        existing_metadata (dict): Existing metadata
        new_metadata (dict): New metadata
        
    Returns:
        dict: Merged metadata
    """
    merged = existing_metadata.copy()
    
    # Merge tags
    if 'tags' in existing_metadata and 'tags' in new_metadata:
        merged['tags'] = list(set(existing_metadata['tags'] + new_metadata['tags']))
    elif 'tags' in new_metadata:
        merged['tags'] = new_metadata['tags']
    
    # Prefer newer dates
    if 'updated_at' in new_metadata:
        merged['updated_at'] = new_metadata['updated_at']
    elif 'updated_at' not in merged:
        merged['updated_at'] = datetime.now().strftime('%Y-%m-%d')
    
    # Merge sources
    if 'source' in existing_metadata and 'source' in new_metadata:
        if isinstance(existing_metadata['source'], list):
            sources = existing_metadata['source']
        else:
            sources = [existing_metadata['source']]
            
        if isinstance(new_metadata['source'], list):
            sources.extend(new_metadata['source'])
        else:
            sources.append(new_metadata['source'])
            
        merged['source'] = list(set(sources))
    elif 'source' in new_metadata:
        merged['source'] = new_metadata['source']
    
    # Merge descriptions
    if 'description' in new_metadata and new_metadata['description']:
        merged['description'] = new_metadata['description']
    
    return merged


def merge_patterns(existing_pattern, new_pattern):
    """
    Merge two pattern definitions.
    
    Args:
        existing_pattern (dict): Existing pattern
        new_pattern (dict): New pattern
        
    Returns:
        dict: Merged pattern
    """
    merged = existing_pattern.copy()
    
    # Merge metadata
    if 'metadata' in existing_pattern and 'metadata' in new_pattern:
        merged['metadata'] = merge_metadata(existing_pattern['metadata'], new_pattern['metadata'])
    elif 'metadata' in new_pattern:
        merged['metadata'] = new_pattern['metadata']
    
    # Prefer higher confidence
    if new_pattern.get('confidence', 0) > existing_pattern.get('confidence', 0):
        merged['confidence'] = new_pattern['confidence']
    
    # Prefer higher priority
    if new_pattern.get('priority', 0) > existing_pattern.get('priority', 0):
        merged['priority'] = new_pattern['priority']
    
    # Merge test cases if they exist
    if 'test_cases' in existing_pattern and 'test_cases' in new_pattern:
        # Combine and deduplicate test cases
        existing_inputs = {tc['input'] for tc in existing_pattern['test_cases']}
        merged_test_cases = existing_pattern['test_cases'][:]
        
        for test_case in new_pattern['test_cases']:
            if test_case['input'] not in existing_inputs:
                merged_test_cases.append(test_case)
                
        merged['test_cases'] = merged_test_cases
    elif 'test_cases' in new_pattern:
        merged['test_cases'] = new_pattern['test_cases']
    
    return merged


def merge_pattern_files(existing_file, new_file):
    """
    Merge two pattern files.
    
    Args:
        existing_file (str): Path to existing pattern file
        new_file (str): Path to new pattern file
    """
    try:
        # Load existing pattern
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Load new pattern
        with open(new_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        # Handle multi-version patterns
        if 'all_versions' in existing_data and 'all_versions' in new_data:
            # Merge all versions
            existing_patterns = {p['name']: p for p in existing_data['all_versions']}
            merged_versions = existing_data['all_versions'][:]
            
            for new_pattern in new_data['all_versions']:
                if new_pattern['name'] in existing_patterns:
                    # Merge with existing pattern
                    existing_pattern = existing_patterns[new_pattern['name']]
                    merged_pattern = merge_patterns(existing_pattern, new_pattern)
                    
                    # Replace in merged list
                    for i, pattern in enumerate(merged_versions):
                        if pattern['name'] == new_pattern['name']:
                            merged_versions[i] = merged_pattern
                            break
                else:
                    # Add new pattern
                    merged_versions.append(new_pattern)
            
            # Update the all_versions field
            existing_data['all_versions'] = merged_versions
            
        elif 'all_versions' in existing_data:
            # Existing is multi-version, new is single
            existing_patterns = {p['name']: p for p in existing_data['all_versions']}
            merged_versions = existing_data['all_versions'][:]
            
            if new_data['name'] in existing_patterns:
                # Merge with existing pattern
                existing_pattern = existing_patterns[new_data['name']]
                merged_pattern = merge_patterns(existing_pattern, new_data)
                
                # Replace in merged list
                for i, pattern in enumerate(merged_versions):
                    if pattern['name'] == new_data['name']:
                        merged_versions[i] = merged_pattern
                        break
            else:
                # Add new pattern
                merged_versions.append(new_data)
                
            existing_data['all_versions'] = merged_versions
            
        else:
            # Both are single version
            if existing_data['name'] == new_data['name']:
                # Merge the patterns
                merged_data = merge_patterns(existing_data, new_data)
                existing_data = merged_data
            else:
                # Convert to multi-version format
                existing_data = {
                    'vendor': existing_data.get('vendor', ''),
                    'vendor_id': existing_data.get('vendor_id', ''),
                    'product': existing_data.get('product', ''),
                    'product_id': existing_data.get('product_id', ''),
                    'category': existing_data.get('category', 'web'),
                    'subcategory': existing_data.get('subcategory', 'web-application'),
                    'versions': {},
                    'all_versions': [existing_data, new_data]
                }
        
        # Save merged pattern
        with open(existing_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        # Remove the new file as it's now merged
        os.remove(new_file)
        
        print(f"Merged {new_file} into {existing_file}")
        
    except Exception as e:
        print(f"Error merging {existing_file} and {new_file}: {e}")


def merge_imported_patterns(import_dir, target_dir):
    """
    Merge patterns from import directory into target directory.
    
    Args:
        import_dir (str): Directory with imported patterns
        target_dir (str): Target directory for merged patterns
    """
    # Walk through imported patterns
    for root, dirs, files in os.walk(import_dir):
        for file in files:
            if file.endswith('.json'):
                import_filepath = os.path.join(root, file)
                # Determine relative path
                rel_path = os.path.relpath(import_filepath, import_dir)
                target_filepath = os.path.join(target_dir, rel_path)
                
                # Check if pattern already exists
                if os.path.exists(target_filepath):
                    # Merge the patterns
                    merge_pattern_files(target_filepath, import_filepath)
                else:
                    # Move the new pattern
                    os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
                    shutil.move(import_filepath, target_filepath)
                    print(f"Moved new pattern to {target_filepath}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Merge imported patterns with existing patterns')
    parser.add_argument('import_dir', help='Directory containing imported patterns')
    parser.add_argument('target_dir', help='Target directory for merged patterns')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.import_dir):
        print(f"Import directory not found: {args.import_dir}")
        return
    
    if not os.path.exists(args.target_dir):
        print(f"Target directory not found: {args.target_dir}")
        return
    
    print(f"Merging patterns from {args.import_dir} into {args.target_dir}")
    merge_imported_patterns(args.import_dir, args.target_dir)
    
    print("Pattern merge completed!")


if __name__ == "__main__":
    main()