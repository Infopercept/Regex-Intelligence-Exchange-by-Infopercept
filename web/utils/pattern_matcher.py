"""
Pattern matching utilities for the Regex Intelligence Exchange web interface.
"""

import re
from typing import List, Dict, Any

def find_matches(input_text: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Find matches for patterns in input text.
    
    Args:
        input_text: Text to search for patterns
        patterns: List of pattern dictionaries
        
    Returns:
        List of match dictionaries.
    """
    matches = []
    
    # Iterate through all patterns
    for pattern_data in patterns:
        vendor = pattern_data.get('vendor', 'Unknown')
        product = pattern_data.get('product', 'Unknown')
        vendor_id = pattern_data.get('vendor_id', 'unknown')
        product_id = pattern_data.get('product_id', 'unknown')
        
        # Check all_versions patterns
        if 'all_versions' in pattern_data:
            for pattern in pattern_data['all_versions']:
                try:
                    regex = re.compile(pattern['pattern'])
                    match = regex.search(input_text)
                    if match:
                        matches.append({
                            'vendor': vendor,
                            'product': product,
                            'vendor_id': vendor_id,
                            'product_id': product_id,
                            'pattern_name': pattern.get('name', 'Unknown'),
                            'matched_text': match.group(0),
                            'version': match.group(pattern['version_group']) if pattern['version_group'] <= len(match.groups()) else None
                        })
                except re.error:
                    # Skip invalid regex patterns
                    continue
        
        # Check version-specific patterns
        if 'versions' in pattern_data:
            for version, version_patterns in pattern_data['versions'].items():
                for pattern in version_patterns:
                    try:
                        regex = re.compile(pattern['pattern'])
                        match = regex.search(input_text)
                        if match:
                            matches.append({
                                'vendor': vendor,
                                'product': product,
                                'vendor_id': vendor_id,
                                'product_id': product_id,
                                'pattern_name': pattern.get('name', 'Unknown'),
                                'matched_text': match.group(0),
                                'version': match.group(pattern['version_group']) if pattern['version_group'] <= len(match.groups()) else None,
                                'version_range': version
                            })
                    except re.error:
                        # Skip invalid regex patterns
                        continue
    
    return matches

def match_single_pattern(input_text: str, pattern_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Match a single pattern against input text.
    
    Args:
        input_text: Text to search for patterns
        pattern_dict: Single pattern dictionary
        
    Returns:
        List of match dictionaries.
    """
    matches = []
    vendor = pattern_dict.get('vendor', 'Unknown')
    product = pattern_dict.get('product', 'Unknown')
    vendor_id = pattern_dict.get('vendor_id', 'unknown')
    product_id = pattern_dict.get('product_id', 'unknown')
    
    # Check all_versions patterns
    if 'all_versions' in pattern_dict:
        for pattern in pattern_dict['all_versions']:
            try:
                regex = re.compile(pattern['pattern'])
                match = regex.search(input_text)
                if match:
                    matches.append({
                        'vendor': vendor,
                        'product': product,
                        'vendor_id': vendor_id,
                        'product_id': product_id,
                        'pattern_name': pattern.get('name', 'Unknown'),
                        'matched_text': match.group(0),
                        'version': match.group(pattern['version_group']) if pattern['version_group'] <= len(match.groups()) else None
                    })
            except re.error:
                # Skip invalid regex patterns
                continue
    
    # Check version-specific patterns
    if 'versions' in pattern_dict:
        for version, version_patterns in pattern_dict['versions'].items():
            for pattern in version_patterns:
                try:
                    regex = re.compile(pattern['pattern'])
                    match = regex.search(input_text)
                    if match:
                        matches.append({
                            'vendor': vendor,
                            'product': product,
                            'vendor_id': vendor_id,
                            'product_id': product_id,
                            'pattern_name': pattern.get('name', 'Unknown'),
                            'matched_text': match.group(0),
                            'version': match.group(pattern['version_group']) if pattern['version_group'] <= len(match.groups()) else None,
                            'version_range': version
                        })
                except re.error:
                    # Skip invalid regex patterns
                    continue
    
    return matches