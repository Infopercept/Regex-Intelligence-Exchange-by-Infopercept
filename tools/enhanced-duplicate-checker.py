#!/usr/bin/env python3
"""
Enhanced duplicate checker with more sophisticated detection algorithms
"""

import json
import os
import hashlib
import re
from collections import defaultdict
from difflib import SequenceMatcher


def calculate_pattern_hash(pattern_data):
    """
    Calculate a hash for a pattern based on its key characteristics.
    
    Args:
        pattern_data (dict): Pattern data
        
    Returns:
        str: Hash of the pattern
    """
    # Extract key fields for comparison
    key_fields = {
        'name': pattern_data.get('name', ''),
        'pattern': pattern_data.get('pattern', ''),
        'vendor': pattern_data.get('vendor', ''),
        'product': pattern_data.get('product', '')
    }
    
    # Create a string representation and hash it
    pattern_str = json.dumps(key_fields, sort_keys=True)
    return hashlib.md5(pattern_str.encode('utf-8')).hexdigest()


def calculate_similarity(pattern1, pattern2):
    """
    Calculate similarity between two patterns.
    
    Args:
        pattern1 (dict): First pattern
        pattern2 (dict): Second pattern
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Compare pattern strings
    pattern1_str = pattern1.get('pattern', '')
    pattern2_str = pattern2.get('pattern', '')
    
    # Use SequenceMatcher for string similarity
    pattern_similarity = SequenceMatcher(None, pattern1_str, pattern2_str).ratio()
    
    # Compare names
    name1 = pattern1.get('name', '')
    name2 = pattern2.get('name', '')
    name_similarity = SequenceMatcher(None, name1, name2).ratio()
    
    # Weighted average (80% pattern similarity, 20% name similarity)
    return 0.8 * pattern_similarity + 0.2 * name_similarity


def normalize_pattern_string(pattern_str):
    """
    Normalize a pattern string for better comparison.
    
    Args:
        pattern_str (str): Pattern string
        
    Returns:
        str: Normalized pattern string
    """
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', pattern_str.strip())
    
    # Normalize escape sequences
    normalized = normalized.replace('\\.', '.')
    normalized = normalized.replace('\\d', '[0-9]')
    normalized = normalized.replace('\\s', '[ \t\n\r\f\v]')
    normalized = normalized.replace('\\w', '[a-zA-Z0-9_]')
    
    return normalized


def find_exact_duplicates(patterns_dir):
    """
    Find exact duplicate patterns in the repository.
    
    Args:
        patterns_dir (str): Directory containing pattern files
        
    Returns:
        dict: Dictionary of duplicate groups
    """
    # Dictionary to store pattern hashes
    pattern_hashes = defaultdict(list)
    
    # Walk through all pattern files
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Handle both single pattern files and multi-version files
                    if 'all_versions' in data:
                        patterns = data['all_versions']
                    else:
                        patterns = [data]
                    
                    # Calculate hash for each pattern
                    for pattern in patterns:
                        pattern_hash = calculate_pattern_hash(pattern)
                        pattern_hashes[pattern_hash].append({
                            'file': filepath,
                            'pattern_name': pattern.get('name', 'Unknown'),
                            'pattern_data': pattern
                        })
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    # Filter to only include actual duplicates (more than one pattern with same hash)
    duplicates = {hash_val: pattern_list for hash_val, pattern_list in pattern_hashes.items() if len(pattern_list) > 1}
    
    return duplicates


def find_similar_patterns(patterns_dir, similarity_threshold=0.8):
    """
    Find similar patterns that might be duplicates.
    
    Args:
        patterns_dir (str): Directory containing pattern files
        similarity_threshold (float): Minimum similarity score to consider patterns similar
        
    Returns:
        list: List of similar pattern groups
    """
    # Collect all patterns
    all_patterns = []
    
    # Walk through all pattern files
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Handle both single pattern files and multi-version files
                    if 'all_versions' in data:
                        patterns = data['all_versions']
                    else:
                        patterns = [data]
                    
                    # Add each pattern
                    for pattern in patterns:
                        all_patterns.append({
                            'file': filepath,
                            'pattern_name': pattern.get('name', 'Unknown'),
                            'pattern_data': pattern
                        })
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    # Find similar patterns
    similar_groups = []
    processed_patterns = set()
    
    for i, pattern1 in enumerate(all_patterns):
        if i in processed_patterns:
            continue
            
        similar_group = [pattern1]
        group_indices = [i]
        
        for j, pattern2 in enumerate(all_patterns[i+1:], i+1):
            if j in processed_patterns:
                continue
                
            similarity = calculate_similarity(pattern1['pattern_data'], pattern2['pattern_data'])
            if similarity >= similarity_threshold:
                similar_group.append(pattern2)
                group_indices.append(j)
        
        # Only consider it a group if there are multiple similar patterns
        if len(similar_group) > 1:
            similar_groups.append(similar_group)
            processed_patterns.update(group_indices)
    
    return similar_groups


def find_duplicate_patterns(patterns_dir):
    """
    Find duplicate patterns in the repository using multiple methods.
    
    Args:
        patterns_dir (str): Directory containing pattern files
    """
    print("Checking for exact duplicates...")
    exact_duplicates = find_exact_duplicates(patterns_dir)
    
    print(f"Found {len(exact_duplicates)} groups of exact duplicate patterns:")
    for pattern_hash, pattern_list in exact_duplicates.items():
        print(f"\nExact duplicate group (hash: {pattern_hash[:8]}):")
        for pattern_info in pattern_list:
            print(f"  - {pattern_info['pattern_name']} in {pattern_info['file']}")
    
    print("\nChecking for similar patterns...")
    similar_patterns = find_similar_patterns(patterns_dir, similarity_threshold=0.85)
    
    print(f"Found {len(similar_patterns)} groups of similar patterns:")
    for i, similar_group in enumerate(similar_patterns):
        print(f"\nSimilar pattern group {i+1}:")
        for pattern_info in similar_group:
            similarity_score = calculate_similarity(similar_group[0]['pattern_data'], pattern_info['pattern_data'])
            print(f"  - {pattern_info['pattern_name']} in {pattern_info['file']} (similarity: {similarity_score:.2f})")
    
    total_duplicates = len(exact_duplicates)
    total_similar = len(similar_patterns)
    
    print(f"\nSummary:")
    print(f"  - Exact duplicate groups: {total_duplicates}")
    print(f"  - Similar pattern groups: {total_similar}")
    print(f"  - Total potential duplicate issues: {total_duplicates + total_similar}")


def main():
    """Main function."""
    patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
    
    if not os.path.exists(patterns_dir):
        print(f"Patterns directory not found: {patterns_dir}")
        return
    
    print("Enhanced duplicate pattern checker")
    print("==================================")
    find_duplicate_patterns(patterns_dir)
    
    print("\nDuplicate check completed!")


if __name__ == "__main__":
    main()