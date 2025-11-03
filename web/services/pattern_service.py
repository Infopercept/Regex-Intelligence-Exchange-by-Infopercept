"""
Simple pattern service for Regex Intelligence Exchange.
"""

import os
import json
import logging
import re
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Simple pattern classes
class Pattern:
    def __init__(self, vendor, product, vendor_id, product_id, category, subcategory=None, versions=None, all_versions=None):
        self.vendor = vendor
        self.product = product
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.category = category
        self.subcategory = subcategory
        self.versions = versions or {}
        self.all_versions = all_versions or []
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            vendor=data.get('vendor', ''),
            product=data.get('product', ''),
            vendor_id=data.get('vendor_id', ''),
            product_id=data.get('product_id', ''),
            category=data.get('category', ''),
            subcategory=data.get('subcategory'),
            versions=data.get('versions', {}),
            all_versions=[VersionPattern.from_dict(v) for v in data.get('all_versions', [])]
        )
    
    def to_dict(self):
        return {
            'vendor': self.vendor,
            'product': self.product,
            'vendor_id': self.vendor_id,
            'product_id': self.product_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'versions': self.versions,
            'all_versions': [v.to_dict() for v in self.all_versions]
        }

class VersionPattern:
    def __init__(self, name, pattern, version_range=None):
        self.name = name
        self.pattern = pattern
        self.version_range = version_range
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get('name', ''),
            pattern=data.get('pattern', ''),
            version_range=data.get('version_range')
        )
    
    def to_dict(self):
        return {
            'name': self.name,
            'pattern': self.pattern,
            'version_range': self.version_range
        }

class PatternSearchResult:
    def __init__(self, patterns, total, offset=0, limit=None):
        self.patterns = patterns
        self.total = total
        self.offset = offset
        self.limit = limit

class PatternMatch:
    def __init__(self, vendor, product, vendor_id, product_id, pattern_name, matched_text, version=None, version_range=None):
        self.vendor = vendor
        self.product = product
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.pattern_name = pattern_name
        self.matched_text = matched_text
        self.version = version
        self.version_range = version_range

class CategoryStats:
    def __init__(self, total_patterns, categories, subcategories):
        self.total_patterns = total_patterns
        self.categories = categories
        self.subcategories = subcategories

class PatternService:
    """Simple file-based pattern service."""
    
    def __init__(self, patterns_dir: str = None):
        self.patterns_dir = patterns_dir or self._get_default_patterns_dir()
        self.compiled_patterns = {}  # Cache for compiled regex patterns
        self.patterns = {}  # File-based pattern storage
        self.load_patterns()
    
    def _get_default_patterns_dir(self) -> str:
        """Get default patterns directory."""
        current_dir = Path(__file__).parent
        return str(current_dir.parent.parent / 'patterns' / 'by-vendor')
    
    def load_patterns(self):
        """Load all patterns from the file system."""
        self.patterns = {}
        
        try:
            for root, dirs, files in os.walk(self.patterns_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                pattern_data = json.load(f)
                            
                            pattern = Pattern.from_dict(pattern_data)
                            pattern_key = f"{pattern.vendor_id}/{pattern.product_id}"
                            self.patterns[pattern_key] = pattern
                            
                        except Exception as e:
                            logger.error(f"Error loading pattern from {file_path}: {e}")
                            continue
            
            logger.info(f"Loaded {len(self.patterns)} patterns from file system")
            
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
    
    def get_all_patterns(self, limit: Optional[int] = None, offset: int = 0) -> List[Pattern]:
        """Get all patterns."""
        try:
            patterns = self._get_patterns_from_files(limit, offset)
            return patterns
        except Exception as e:
            logger.error(f"Error getting patterns: {e}")
            return []
    
    def _get_patterns_from_files(self, limit: Optional[int] = None, offset: int = 0) -> List[Pattern]:
        """Get patterns from files."""
        patterns = list(self.patterns.values())
        
        # Sort for consistent ordering
        patterns.sort(key=lambda p: (p.vendor, p.product))
        
        # Apply offset and limit
        if offset:
            patterns = patterns[offset:]
        if limit:
            patterns = patterns[:limit]
        
        return patterns
    
    def get_pattern_by_id(self, vendor_id: str, product_id: str) -> Optional[Pattern]:
        """Get pattern by vendor and product ID."""
        try:
            pattern_key = f"{vendor_id}/{product_id}"
            return self.patterns.get(pattern_key)
        except Exception as e:
            logger.error(f"Error getting pattern {vendor_id}/{product_id}: {e}")
            return None
    
    def search_patterns(self, query: Optional[str] = None, category: Optional[str] = None, 
                       vendor: Optional[str] = None, limit: Optional[int] = None, 
                       offset: int = 0) -> PatternSearchResult:
        """Search patterns with filters."""
        try:
            all_patterns = list(self.patterns.values())
            patterns = self._filter_patterns(all_patterns, query, category, vendor)
            
            # Apply pagination
            total = len(patterns)
            if offset:
                patterns = patterns[offset:]
            if limit:
                patterns = patterns[:limit]
            
            return PatternSearchResult(
                patterns=patterns,
                total=total,
                offset=offset,
                limit=limit
            )
            
        except Exception as e:
            logger.error(f"Error searching patterns: {e}")
            return PatternSearchResult(patterns=[], total=0, offset=offset, limit=limit)
    
    def _filter_patterns(self, patterns: List[Pattern], query: Optional[str] = None, 
                        category: Optional[str] = None, vendor: Optional[str] = None) -> List[Pattern]:
        """Filter patterns based on criteria."""
        filtered = patterns
        
        if category:
            category_lower = category.lower()
            filtered = [p for p in filtered if category_lower in p.category.lower()]
        
        if vendor:
            vendor_lower = vendor.lower()
            filtered = [p for p in filtered if vendor_lower in p.vendor.lower()]
        
        if query:
            query_lower = query.lower()
            filtered = [
                p for p in filtered
                if (query_lower in p.vendor.lower() or 
                    query_lower in p.product.lower() or 
                    query_lower in p.category.lower() or
                    query_lower in (p.subcategory or "").lower())
            ]
        
        return filtered
    
    def match_patterns(self, input_text: str, max_patterns: int = 100) -> List[PatternMatch]:
        """Match patterns against input text."""
        matches = []
        
        try:
            patterns = self.get_all_patterns(limit=max_patterns)
            
            for pattern in patterns:
                # Check all versions
                for version_patterns in pattern.versions.values():
                    for version_pattern in version_patterns:
                        match_result = self._test_pattern_match(version_pattern.pattern, input_text)
                        if match_result:
                            match = PatternMatch(
                                vendor=pattern.vendor,
                                product=pattern.product,
                                vendor_id=pattern.vendor_id,
                                product_id=pattern.product_id,
                                pattern_name=version_pattern.name,
                                matched_text=match_result['matched_text'],
                                version=match_result.get('version'),
                                version_range=match_result.get('version_range')
                            )
                            matches.append(match)
                            break  # Only one match per pattern
                
                # Also check all_versions
                for version_pattern in pattern.all_versions:
                    match_result = self._test_pattern_match(version_pattern.pattern, input_text)
                    if match_result:
                        # Check if we already have a match for this pattern
                        existing_match = any(
                            m.vendor_id == pattern.vendor_id and m.product_id == pattern.product_id
                            for m in matches
                        )
                        if not existing_match:
                            match = PatternMatch(
                                vendor=pattern.vendor,
                                product=pattern.product,
                                vendor_id=pattern.vendor_id,
                                product_id=pattern.product_id,
                                pattern_name=version_pattern.name,
                                matched_text=match_result['matched_text'],
                                version=match_result.get('version'),
                                version_range=match_result.get('version_range')
                            )
                            matches.append(match)
                            break
            
            return matches
            
        except Exception as e:
            logger.error(f"Error matching patterns: {e}")
            return []
    
    def _test_pattern_match(self, pattern: str, text: str) -> Optional[Dict[str, Any]]:
        """Test if pattern matches text."""
        try:
            # Use compiled pattern cache for better performance
            if pattern not in self.compiled_patterns:
                self.compiled_patterns[pattern] = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            
            compiled_pattern = self.compiled_patterns[pattern]
            match = compiled_pattern.search(text)
            
            if match:
                result = {
                    'matched_text': match.group(0),
                    'full_match': match
                }
                
                # Try to extract version if there are groups
                if match.groups():
                    # Assume first group is version
                    result['version'] = match.group(1)
                
                return result
            
        except re.error as e:
            logger.warning(f"Invalid regex pattern: {pattern} - {e}")
        except Exception as e:
            logger.error(f"Error testing pattern match: {e}")
        
        return None
    
    def get_statistics(self) -> CategoryStats:
        """Get pattern statistics."""
        try:
            patterns = list(self.patterns.values())
            
            categories = {}
            subcategories = {}
            
            for pattern in patterns:
                # Count categories
                if pattern.category:
                    categories[pattern.category] = categories.get(pattern.category, 0) + 1
                
                # Count subcategories
                if pattern.subcategory:
                    subcategories[pattern.subcategory] = subcategories.get(pattern.subcategory, 0) + 1
            
            return CategoryStats(
                total_patterns=len(patterns),
                categories=categories,
                subcategories=subcategories
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return CategoryStats(total_patterns=0, categories={}, subcategories={})
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status."""
        status = {
            'service': 'healthy',
            'patterns_loaded': len(self.patterns),
            'compiled_patterns': len(self.compiled_patterns),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if len(self.patterns) == 0:
                status['service'] = 'unhealthy'
                status['error'] = 'No patterns loaded'
        except Exception as e:
            status['service'] = 'unhealthy'
            status['error'] = str(e)
        
        return status

# Global pattern service instance
pattern_service = PatternService()