"""
Version utilities for the Regex Intelligence Exchange web interface.
"""

import re
from typing import Optional
from packaging import version

def normalize_version(version_str: str) -> Optional[str]:
    """
    Normalize a version string to a standard format.
    
    Args:
        version_str: The version string to normalize
        
    Returns:
        Normalized version string or None if invalid
    """
    if not version_str:
        return None
    
    # Remove common prefixes
    version_str = version_str.strip()
    version_str = re.sub(r'^[vVrR]', '', version_str)
    
    # Handle common version formats
    # Extract version numbers and dots only
    version_match = re.search(r'(\d+(?:\.\d+)*)', version_str)
    if version_match:
        normalized = version_match.group(1)
        # Validate using packaging.version
        try:
            version.parse(normalized)
            return normalized
        except version.InvalidVersion:
            return None
    
    return None

def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    
    Args:
        version1: First version string
        version2: Second version string
        
    Returns:
        -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    try:
        v1 = version.parse(version1)
        v2 = version.parse(version2)
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    except version.InvalidVersion:
        # If we can't parse the versions, do string comparison
        if version1 < version2:
            return -1
        elif version1 > version2:
            return 1
        else:
            return 0

def is_version_in_range(version_str: str, version_range: str) -> bool:
    """
    Check if a version is within a specified range.
    
    Args:
        version_str: Version to check
        version_range: Version range string (e.g., ">=1.0.0,<2.0.0")
        
    Returns:
        True if version is in range, False otherwise
    """
    try:
        v = version.parse(version_str)
        
        # Simple range parsing
        if ',' in version_range:
            # Multiple conditions
            conditions = version_range.split(',')
            for condition in conditions:
                if not _check_single_condition(v, condition.strip()):
                    return False
            return True
        else:
            # Single condition
            return _check_single_condition(v, version_range)
    except version.InvalidVersion:
        return False

def _check_single_condition(version_obj, condition: str) -> bool:
    """
    Check a single version condition.
    
    Args:
        version_obj: Parsed version object
        condition: Condition string (e.g., ">=1.0.0")
        
    Returns:
        True if condition is met, False otherwise
    """
    if condition.startswith('>='):
        try:
            min_version = version.parse(condition[2:])
            return version_obj >= min_version
        except version.InvalidVersion:
            return False
    elif condition.startswith('>'):
        try:
            min_version = version.parse(condition[1:])
            return version_obj > min_version
        except version.InvalidVersion:
            return False
    elif condition.startswith('<='):
        try:
            max_version = version.parse(condition[2:])
            return version_obj <= max_version
        except version.InvalidVersion:
            return False
    elif condition.startswith('<'):
        try:
            max_version = version.parse(condition[1:])
            return version_obj < max_version
        except version.InvalidVersion:
            return False
    elif condition.startswith('=='):
        try:
            eq_version = version.parse(condition[2:])
            return version_obj == eq_version
        except version.InvalidVersion:
            return False
    else:
        # Assume exact match
        try:
            eq_version = version.parse(condition)
            return version_obj == eq_version
        except version.InvalidVersion:
            return False