#!/usr/bin/env python3
"""
Version utilities for processing and normalizing software versions extracted from patterns
"""

import re
from packaging import version


def normalize_version(version_str):
    """
    Normalize a version string to a standard format.
    
    Args:
        version_str (str): The version string to normalize
        
    Returns:
        str: Normalized version string or None if invalid
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


def extract_and_normalize_version(match, version_group):
    """
    Extract and normalize version from a regex match.
    
    Args:
        match: Regex match object
        version_group (int): The capture group containing the version
        
    Returns:
        str: Normalized version string or None if extraction fails
    """
    if not match or version_group <= 0 or version_group > len(match.groups()):
        return None
    
    raw_version = match.group(version_group)
    return normalize_version(raw_version)


def compare_versions(version1, version2):
    """
    Compare two version strings.
    
    Args:
        version1 (str): First version string
        version2 (str): Second version string
        
    Returns:
        int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
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


def is_version_in_range(version_str, version_range):
    """
    Check if a version is within a specified range.
    
    Args:
        version_str (str): Version to check
        version_range (str): Version range in format like "2.4.x" or ">=1.0.0 <2.0.0"
        
    Returns:
        bool: True if version is in range, False otherwise
    """
    try:
        # Handle simple range formats like "2.4.x"
        if version_range.endswith('.x'):
            prefix = version_range[:-2]
            return version_str.startswith(prefix)
        
        # Handle more complex ranges like ">=1.0.0 <2.0.0"
        # This is a simplified implementation
        normalized_version = version.parse(version_str)
        
        # For now, we'll just check if the version can be parsed
        # A full implementation would parse the range syntax
        return True
    except version.InvalidVersion:
        return False


def get_version_parts(version_str):
    """
    Split a version string into its component parts.
    
    Args:
        version_str (str): Version string
        
    Returns:
        dict: Dictionary with major, minor, patch, and additional parts
    """
    normalized = normalize_version(version_str)
    if not normalized:
        return None
    
    parts = normalized.split('.')
    result = {
        'major': parts[0] if len(parts) > 0 else None,
        'minor': parts[1] if len(parts) > 1 else None,
        'patch': parts[2] if len(parts) > 2 else None,
        'full': normalized
    }
    
    # Handle additional parts like pre-release identifiers
    if len(parts) > 3:
        result['additional'] = '.'.join(parts[3:])
    
    return result


# Example usage and testing
if __name__ == "__main__":
    # Test version normalization
    test_versions = [
        "2.4.41",
        "v2.4.41",
        "V2.4.41",
        "r2.4.41",
        "2.4.41 (Ubuntu)",
        "2.4.41-alpha",
        "invalid"
    ]
    
    print("Version Normalization Tests:")
    for v in test_versions:
        normalized = normalize_version(v)
        print(f"  {v} -> {normalized}")
    
    print("\nVersion Comparison Tests:")
    comparisons = [
        ("2.4.41", "2.4.40"),
        ("2.4.41", "2.4.41"),
        ("2.4.40", "2.4.41")
    ]
    
    for v1, v2 in comparisons:
        result = compare_versions(v1, v2)
        print(f"  {v1} vs {v2} -> {result}")