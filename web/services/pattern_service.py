"""
Pattern service for Regex Intelligence Exchange.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from models.pattern import Pattern, PatternSearchResult, PatternMatch, CategoryStats
from utils.logging import log_manager
from utils.cache import pattern_cache

class PatternService:
    """Service for managing patterns."""
    
    def __init__(self, patterns_dir: Optional[str] = None):
        self.patterns_dir = patterns_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            '..', 'patterns', 'by-vendor'
        )
        self._patterns_cache: Dict[str, Pattern] = {}
        self._loaded = False
    
    def load_patterns(self) -> List[Pattern]:
        """Load all pattern files into memory."""
        # Check if patterns are cached
        cached_patterns = pattern_cache.get_patterns()
        if cached_patterns and not pattern_cache.is_expired():
            log_manager.info("Using cached patterns")
            return list(cached_patterns.values())
        
        if self._loaded and self._patterns_cache:
            return list(self._patterns_cache.values())
        
        patterns = []
        self._patterns_cache = {}
        
        for root, dirs, files in os.walk(self.patterns_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            pattern_data = json.load(f)
                            pattern = Pattern.from_dict(pattern_data)
                            pattern_key = f"{pattern.vendor_id}/{pattern.product_id}"
                            self._patterns_cache[pattern_key] = pattern
                            patterns.append(pattern)
                    except Exception as e:
                        log_manager.error(f"Error loading pattern file {file_path}: {e}")
        
        self._loaded = True
        
        # Cache the patterns
        pattern_cache.update_patterns(self._patterns_cache)
        
        log_manager.info(f"Loaded {len(patterns)} patterns")
        return patterns
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns."""
        return self.load_patterns()
    
    def get_pattern_by_id(self, vendor_id: str, product_id: str) -> Optional[Pattern]:
        """Get a specific pattern by vendor and product ID."""
        if not self._loaded:
            self.load_patterns()
        
        pattern_key = f"{vendor_id}/{product_id}"
        return self._patterns_cache.get(pattern_key)
    
    def search_patterns(self, query: str = '', category: str = '', vendor: str = '') -> PatternSearchResult:
        """Search patterns with optional filtering."""
        patterns = self.get_all_patterns()
        
        # Filter patterns
        filtered_patterns = patterns
        
        if category:
            filtered_patterns = [p for p in filtered_patterns if p.category.lower() == category.lower()]
        
        if vendor:
            # Check both vendor name and vendor_id for matching
            filtered_patterns = [p for p in filtered_patterns if p.vendor.lower() == vendor.lower() or p.vendor_id.lower() == vendor.lower()]
        
        if query:
            query = query.lower()
            filtered_patterns = [
                p for p in filtered_patterns 
                if query in p.vendor.lower() or 
                   query in p.product.lower() or
                   query in p.category.lower() or
                   query in p.subcategory.lower() or
                   query in p.vendor_id.lower() or
                   query in p.product_id.lower()
            ]
        
        return PatternSearchResult(
            patterns=filtered_patterns,
            total=len(filtered_patterns)
        )
    
    def match_patterns(self, input_text: str) -> List[PatternMatch]:
        """Match patterns against input text."""
        patterns = self.get_all_patterns()
        matches = []
        
        # Iterate through all patterns
        for pattern_obj in patterns:
            vendor = pattern_obj.vendor
            product = pattern_obj.product
            vendor_id = pattern_obj.vendor_id
            product_id = pattern_obj.product_id
            
            # Check all_versions patterns
            for pattern in pattern_obj.all_versions:
                try:
                    regex = re.compile(pattern.pattern, re.IGNORECASE)
                    match = regex.search(input_text)
                    if match:
                        # Extract version if version_group is valid
                        version = None
                        if pattern.version_group > 0 and pattern.version_group <= len(match.groups()):
                            version = match.group(pattern.version_group)
                        
                        matches.append(PatternMatch(
                            vendor=vendor,
                            product=product,
                            vendor_id=vendor_id,
                            product_id=product_id,
                            pattern_name=pattern.name,
                            matched_text=match.group(0),
                            version=version
                        ))
                except re.error as e:
                    # Log invalid regex patterns but continue
                    log_manager.error(f"Invalid regex pattern in {vendor}/{product}: {pattern.pattern} - {e}")
                    continue
            
            # Check version-specific patterns
            for version_range, version_patterns in pattern_obj.versions.items():
                for pattern in version_patterns:
                    try:
                        regex = re.compile(pattern.pattern, re.IGNORECASE)
                        match = regex.search(input_text)
                        if match:
                            # Extract version if version_group is valid
                            version = None
                            if pattern.version_group > 0 and pattern.version_group <= len(match.groups()):
                                version = match.group(pattern.version_group)
                            
                            matches.append(PatternMatch(
                                vendor=vendor,
                                product=product,
                                vendor_id=vendor_id,
                                product_id=product_id,
                                pattern_name=pattern.name,
                                matched_text=match.group(0),
                                version=version,
                                version_range=version_range
                            ))
                    except re.error as e:
                        # Log invalid regex patterns but continue
                        log_manager.error(f"Invalid regex pattern in {vendor}/{product} version {version_range}: {pattern.pattern} - {e}")
                        continue
        
        return matches
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        # Check cache first
        cached_categories = pattern_cache.get_categories()
        if cached_categories is not None:
            return cached_categories
        
        patterns = self.get_all_patterns()
        categories = set()
        for pattern in patterns:
            if pattern.category:
                categories.add(pattern.category)
        
        category_list = sorted(list(categories))
        
        # Cache the categories
        pattern_cache.update_categories(category_list)
        
        return category_list
    
    def get_vendors(self) -> List[str]:
        """Get all available vendors."""
        # Check cache first
        cached_vendors = pattern_cache.get_vendors()
        if cached_vendors is not None:
            return cached_vendors
        
        patterns = self.get_all_patterns()
        vendors = set()
        for pattern in patterns:
            if pattern.vendor:
                vendors.add(pattern.vendor)
        
        vendor_list = sorted(list(vendors))
        
        # Cache the vendors
        pattern_cache.update_vendors(vendor_list)
        
        return vendor_list
    
    def get_statistics(self) -> CategoryStats:
        """Get database statistics."""
        # Check cache first
        cached_stats = pattern_cache.get_stats()
        if cached_stats is not None:
            return CategoryStats(**cached_stats)
        
        patterns = self.get_all_patterns()
        total_patterns = len(patterns)
        
        # Count by category
        category_counts = {}
        for pattern in patterns:
            category = pattern.category or 'unknown'
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by subcategory
        subcategory_counts = {}
        for pattern in patterns:
            subcategory = pattern.subcategory or 'unknown'
            subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1
        
        stats = CategoryStats(
            total_patterns=total_patterns,
            categories=category_counts,
            subcategories=subcategory_counts
        )
        
        # Cache the stats
        pattern_cache.update_stats(stats.__dict__)
        
        return stats
    
    def reload_patterns(self) -> None:
        """Reload all patterns from disk."""
        self._loaded = False
        self._patterns_cache = {}
        
        # Clear the cache
        pattern_cache.clear()
        
        self.load_patterns()
        log_manager.info("Patterns reloaded from disk")

# Global pattern service instance
pattern_service = PatternService()