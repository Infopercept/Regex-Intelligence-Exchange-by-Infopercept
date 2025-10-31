"""
Pattern loading utilities for the Regex Intelligence Exchange web interface.
"""

import json
import os
from typing import List, Dict, Any, Optional

def load_patterns(patterns_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load all pattern files into memory.
    
    Args:
        patterns_dir: Path to patterns directory. If None, uses default location.
        
    Returns:
        List of pattern dictionaries.
    """
    if patterns_dir is None:
        # Default to project patterns directory
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'patterns', 'by-vendor')
    
    patterns = []
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pattern_data = json.load(f)
                        patterns.append(pattern_data)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
    
    return patterns

def get_pattern_by_id(vendor_id: str, product_id: str, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get a specific pattern by vendor and product ID.
    
    Args:
        vendor_id: Vendor ID to search for
        product_id: Product ID to search for
        patterns: List of pattern dictionaries
        
    Returns:
        Pattern dictionary or empty dict if not found.
    """
    for pattern in patterns:
        if (pattern.get('vendor_id') == vendor_id and 
            pattern.get('product_id') == product_id):
            return pattern
    
    return {}

def search_patterns(query: str = '', category: str = '', vendor: str = '', patterns: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Search patterns with optional filtering.
    
    Args:
        query: Search query string
        category: Filter by category
        vendor: Filter by vendor
        patterns: List of pattern dictionaries to search in
        
    Returns:
        List of matching pattern dictionaries.
    """
    if patterns is None:
        patterns = load_patterns()
    
    results = []
    query = query.lower() if query else ''
    
    for pattern in patterns:
        # Filter by query
        if query:
            if (query not in pattern.get('vendor', '').lower() and 
                query not in pattern.get('product', '').lower() and
                query not in pattern.get('category', '').lower()):
                continue
        
        # Filter by category
        if category and pattern.get('category', '') != category:
            continue
            
        # Filter by vendor
        if vendor and pattern.get('vendor', '') != vendor:
            continue
            
        results.append(pattern)
    
    return results

def get_categories(patterns: List[Dict[str, Any]]) -> List[str]:
    """
    Get all available categories from patterns.
    
    Args:
        patterns: List of pattern dictionaries
        
    Returns:
        List of unique categories.
    """
    categories = set()
    for pattern in patterns:
        category = pattern.get('category')
        if category:
            categories.add(category)
    
    return sorted(list(categories))

def get_vendors(patterns: List[Dict[str, Any]]) -> List[str]:
    """
    Get all available vendors from patterns.
    
    Args:
        patterns: List of pattern dictionaries
        
    Returns:
        List of unique vendors.
    """
    vendors = set()
    for pattern in patterns:
        vendor = pattern.get('vendor')
        if vendor:
            vendors.add(vendor)
    
    return sorted(list(vendors))

def get_statistics(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get database statistics.
    
    Args:
        patterns: List of pattern dictionaries
        
    Returns:
        Dictionary with statistics.
    """
    total_patterns = len(patterns)
    
    # Count by category
    category_counts = {}
    for pattern in patterns:
        category = pattern.get('category', 'unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Count by subcategory
    subcategory_counts = {}
    for pattern in patterns:
        subcategory = pattern.get('subcategory', 'unknown')
        subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1
    
    return {
        'total_patterns': total_patterns,
        'categories': category_counts,
        'subcategories': subcategory_counts
    }