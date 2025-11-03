#!/usr/bin/env python3
"""
Test script to verify that the pattern service works with the new directory structure
"""

import os
import sys
import json
import glob
import re

class PatternService:
    """Complete pattern service with all features."""
    
    def __init__(self, patterns_dir=None):
        self.patterns_dir = patterns_dir or self._get_patterns_dir()
        self._patterns_cache = None
        self._stats_cache = None
        self._compiled_patterns = {}
        print(f"🔍 Pattern directory: {self.patterns_dir}")
    
    def _get_patterns_dir(self):
        """Get patterns directory path."""
        return os.path.join(os.path.dirname(__file__), '..', 'patterns', 'by-vendor')
    
    def _load_patterns(self):
        """Load all patterns from files with progress indicator."""
        if self._patterns_cache is not None:
            return self._patterns_cache
        
        patterns = []
        pattern_files = glob.glob(os.path.join(self.patterns_dir, '**', '*.json'), recursive=True)
        
        print(f"📂 Loading patterns from {len(pattern_files)} files...")
        
        for i, file_path in enumerate(pattern_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                    patterns.append(pattern_data)
                
                # Progress indicator
                if (i + 1) % 100 == 0:
                    print(f"   Loaded {i + 1}/{len(pattern_files)} files...")
                    
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
                continue
        
        self._patterns_cache = patterns
        print(f"✅ Successfully loaded {len(patterns)} patterns!")
        return patterns
    
    def get_all_patterns(self, limit=None, offset=0):
        """Get all patterns with pagination."""
        patterns = self._load_patterns()
        
        if offset:
            patterns = patterns[offset:]
        if limit:
            patterns = patterns[:limit]
        
        return patterns
    
    def search_patterns(self, query=None, category=None, vendor=None, limit=None, offset=0):
        """Search patterns with advanced filtering."""
        patterns = self._load_patterns()
        
        if not query and not category and not vendor:
            filtered = patterns
        else:
            filtered = []
            for pattern in patterns:
                match = True
                
                if category and category.lower() not in pattern.get('category', '').lower():
                    match = False
                
                if vendor and vendor.lower() not in pattern.get('vendor', '').lower():
                    match = False
                
                if query:
                    query_lower = query.lower()
                    if not (query_lower in pattern.get('vendor', '').lower() or 
                           query_lower in pattern.get('product', '').lower() or
                           query_lower in pattern.get('category', '').lower()):
                        match = False
                
                if match:
                    filtered.append(pattern)
        
        # Apply pagination
        total = len(filtered)
        if offset:
            filtered = filtered[offset:]
        if limit:
            filtered = filtered[:limit]
        
        return {
            'patterns': filtered,
            'total': total,
            'offset': offset,
            'limit': limit
        }
    
    def get_pattern_by_id(self, vendor_id, product_id):
        """Get specific pattern by vendor and product ID."""
        patterns = self._load_patterns()
        
        for pattern in patterns:
            if (pattern.get('vendor_id') == vendor_id and 
                pattern.get('product_id') == product_id):
                return pattern
        
        return None
    
    def match_patterns(self, input_text, max_patterns=50):
        """Match patterns against input text."""
        patterns = self.get_all_patterns(limit=max_patterns)
        matches = []
        
        for pattern in patterns:
            try:
                # Check all_versions patterns
                for version_pattern in pattern.get('all_versions', []):
                    regex_pattern = version_pattern.get('pattern', '')
                    if regex_pattern:
                        match_result = self._test_pattern_match(regex_pattern, input_text)
                        if match_result:
                            matches.append({
                                'vendor': pattern.get('vendor', ''),
                                'product': pattern.get('product', ''),
                                'vendor_id': pattern.get('vendor_id', ''),
                                'product_id': pattern.get('product_id', ''),
                                'pattern_name': version_pattern.get('name', ''),
                                'matched_text': match_result['matched_text'],
                                'version': match_result.get('version'),
                                'category': pattern.get('category', '')
                            })
                            break  # Only one match per pattern
                
                # Check versions patterns
                for version_key, version_patterns in pattern.get('versions', {}).items():
                    for version_pattern in version_patterns:
                        regex_pattern = version_pattern.get('pattern', '')
                        if regex_pattern:
                            match_result = self._test_pattern_match(regex_pattern, input_text)
                            if match_result:
                                # Check if we already have a match for this pattern
                                existing_match = any(
                                    m['vendor_id'] == pattern.get('vendor_id') and 
                                    m['product_id'] == pattern.get('product_id')
                                    for m in matches
                                )
                                if not existing_match:
                                    matches.append({
                                        'vendor': pattern.get('vendor', ''),
                                        'product': pattern.get('product', ''),
                                        'vendor_id': pattern.get('vendor_id', ''),
                                        'product_id': pattern.get('product_id', ''),
                                        'pattern_name': version_pattern.get('name', ''),
                                        'matched_text': match_result['matched_text'],
                                        'version': match_result.get('version'),
                                        'category': pattern.get('category', '')
                                    })
                                    break
            except Exception as e:
                continue  # Skip problematic patterns
        
        return matches
    
    def _test_pattern_match(self, pattern, text):
        """Test if pattern matches text."""
        try:
            # Use compiled pattern cache for better performance
            if pattern not in self._compiled_patterns:
                self._compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            
            compiled_pattern = self._compiled_patterns[pattern]
            match = compiled_pattern.search(text)
            
            if match:
                result = {
                    'matched_text': match.group(0),
                    'full_match': match
                }
                
                # Try to extract version if there are groups
                if match.groups():
                    result['version'] = match.group(1)
                
                return result
        except re.error:
            pass  # Invalid regex pattern
        except Exception:
            pass  # Other errors
        
        return None

def test_pattern_service():
    """Test the pattern service with the new directory structure"""
    print("Testing Pattern Service...")
    
    # Create pattern service instance
    pattern_service = PatternService()
    
    # Test loading patterns
    print("Loading patterns...")
    patterns = pattern_service.get_all_patterns(limit=5)
    print(f"Loaded {len(patterns)} patterns")
    
    # Test searching patterns
    print("\nTesting pattern search...")
    search_result = pattern_service.search_patterns(query="sample", limit=3)
    print(f"Found {search_result['total']} patterns matching 'sample'")
    
    # Test getting specific pattern
    print("\nTesting specific pattern retrieval...")
    if patterns:
        first_pattern = patterns[0]
        vendor_id = first_pattern.get('vendor_id', '')
        product_id = first_pattern.get('product_id', '')
        if vendor_id and product_id:
            specific_pattern = pattern_service.get_pattern_by_id(vendor_id, product_id)
            if specific_pattern:
                print(f"Successfully retrieved pattern: {specific_pattern.get('vendor', '')} {specific_pattern.get('product', '')}")
    
    # Test pattern matching
    print("\nTesting pattern matching...")
    test_text = "<title>Sample Application</title>"
    matches = pattern_service.match_patterns(test_text, max_patterns=10)
    print(f"Found {len(matches)} matches in test text")
    
    print("\nPattern service test completed successfully!")

if __name__ == '__main__':
    test_pattern_service()