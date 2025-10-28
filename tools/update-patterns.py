#!/usr/bin/env python3
"""
Script to update existing patterns to conform to the enhanced pattern structure
"""

import json
import os
import sys
from pathlib import Path


def update_pattern_structure(pattern_data):
    """
    Update a pattern to conform to the enhanced structure.
    
    Args:
        pattern_data (dict): Pattern data to update
        
    Returns:
        dict: Updated pattern data
    """
    # Ensure all required fields are present
    if 'version_group' not in pattern_data:
        pattern_data['version_group'] = 0
    
    if 'priority' not in pattern_data:
        pattern_data['priority'] = 100
    
    if 'confidence' not in pattern_data:
        pattern_data['confidence'] = 0.8
    
    if 'name' not in pattern_data:
        pattern_data['name'] = "Unnamed Pattern"
    
    # Ensure metadata has all required fields
    if 'metadata' not in pattern_data:
        pattern_data['metadata'] = {
            "author": "Unknown",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-01",
            "description": "Automatically updated pattern",
            "tags": ["auto-updated"]
        }
    else:
        metadata = pattern_data['metadata']
        if 'author' not in metadata:
            metadata['author'] = "Unknown"
        if 'created_at' not in metadata:
            metadata['created_at'] = "2025-01-01"
        if 'updated_at' not in metadata:
            metadata['updated_at'] = "2025-01-01"
        if 'description' not in metadata:
            metadata['description'] = "Automatically updated pattern"
        if 'tags' not in metadata:
            metadata['tags'] = ["auto-updated"]
        elif not isinstance(metadata['tags'], list):
            metadata['tags'] = [metadata['tags']]
    
    return pattern_data


def update_file_structure(file_data):
    """
    Update a pattern file to conform to the enhanced structure.
    
    Args:
        file_data (dict): Pattern file data to update
        
    Returns:
        dict: Updated pattern file data
    """
    # Ensure top-level fields are present
    if 'subcategory' not in file_data:
        # Set subcategory based on category
        category = file_data.get('category', 'web')
        subcategory_mapping = {
            'web': 'web-application',
            'cms': 'cms-platform',
            'database': 'database-engine',
            'framework': 'web-framework',
            'messaging': 'email-server',
            'networking': 'router',
            'os': 'linux-distribution'
        }
        file_data['subcategory'] = subcategory_mapping.get(category, 'web-application')
    
    # Update all_versions patterns
    if 'all_versions' in file_data:
        updated_patterns = []
        for pattern in file_data['all_versions']:
            updated_patterns.append(update_pattern_structure(pattern))
        file_data['all_versions'] = updated_patterns
    
    # Update version-specific patterns
    if 'versions' in file_data:
        updated_versions = {}
        for version_range, patterns in file_data['versions'].items():
            updated_patterns = []
            for pattern in patterns:
                updated_patterns.append(update_pattern_structure(pattern))
            updated_versions[version_range] = updated_patterns
        file_data['versions'] = updated_versions
    
    return file_data


def update_pattern_file(file_path):
    """
    Update a pattern file to conform to the enhanced structure.
    
    Args:
        file_path (str): Path to the pattern file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update the structure
        updated_data = update_file_structure(data)
        
        # Write the updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"Updated {file_path}")
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def find_pattern_files(root_dir):
    """Find all pattern files in the repository."""
    pattern_files = []
    patterns_dir = os.path.join(root_dir, 'patterns')
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                pattern_files.append(os.path.join(root, file))
    
    return pattern_files


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
        
        if update_pattern_file(file_path):
            print(f"Successfully updated {file_path}")
            return 0
        else:
            print(f"Failed to update {file_path}")
            return 1
    else:
        print("Updating all pattern files to enhanced structure...")
        
        # Find all pattern files
        pattern_files = find_pattern_files(repo_root)
        
        if not pattern_files:
            print("No pattern files found!")
            return 1
        
        print(f"Found {len(pattern_files)} pattern files to update")
        
        # Update each pattern file
        updated_files = 0
        failed_files = 0
        
        for pattern_file in pattern_files:
            try:
                if update_pattern_file(pattern_file):
                    updated_files += 1
                else:
                    failed_files += 1
            except Exception as e:
                print(f"Error updating {pattern_file}: {e}")
                failed_files += 1
        
        print(f"\nUpdate Results: {updated_files} updated, {failed_files} failed")
        
        if failed_files > 0:
            return 1
        else:
            return 0


if __name__ == "__main__":
    sys.exit(main())