"""
Database-based pattern service for Regex Intelligence Exchange.
"""

import re
from typing import List, Dict, Any, Optional
from models.database import DatabaseManager
from models.pattern import Pattern, PatternSearchResult, PatternMatch, CategoryStats
from utils.logging import log_manager

class DatabasePatternService:
    """Service for managing patterns using database."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.db_manager = DatabaseManager(database_url) if database_url else DatabaseManager()
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns from database."""
        try:
            db_patterns = self.db_manager.get_all_patterns()
            patterns = []
            
            for db_pattern in db_patterns:
                # Convert database pattern to our Pattern model
                pattern = Pattern(
                    vendor=str(db_pattern.vendor),
                    vendor_id=str(db_pattern.vendor_id),
                    product=str(db_pattern.product),
                    product_id=str(db_pattern.product_id),
                    category=str(db_pattern.category),
                    subcategory=str(db_pattern.subcategory) if db_pattern.subcategory is not None else ""
                )
                patterns.append(pattern)
            
            log_manager.info(f"Loaded {len(patterns)} patterns from database")
            return patterns
        except Exception as e:
            log_manager.error(f"Error loading patterns from database: {e}")
            return []
    
    def get_pattern_by_id(self, vendor_id: str, product_id: str) -> Optional[Pattern]:
        """Get a specific pattern by vendor and product ID."""
        try:
            db_pattern = self.db_manager.get_pattern_by_id(vendor_id, product_id)
            if not db_pattern:
                return None
            
            # Convert to our Pattern model
            pattern = Pattern(
                vendor=str(db_pattern.vendor),
                vendor_id=str(db_pattern.vendor_id),
                product=str(db_pattern.product),
                product_id=str(db_pattern.product_id),
                category=str(db_pattern.category),
                subcategory=str(db_pattern.subcategory) if db_pattern.subcategory is not None else ""
            )
            
            return pattern
        except Exception as e:
            log_manager.error(f"Error getting pattern {vendor_id}/{product_id}: {e}")
            return None
    
    def search_patterns(self, query: str = '', category: str = '', vendor: str = '') -> PatternSearchResult:
        """Search patterns with optional filtering."""
        try:
            db_patterns = self.db_manager.search_patterns(query, category, vendor)
            patterns = []
            
            for db_pattern in db_patterns:
                # Convert database pattern to our Pattern model
                pattern = Pattern(
                    vendor=str(db_pattern.vendor),
                    vendor_id=str(db_pattern.vendor_id),
                    product=str(db_pattern.product),
                    product_id=str(db_pattern.product_id),
                    category=str(db_pattern.category),
                    subcategory=str(db_pattern.subcategory) if db_pattern.subcategory is not None else ""
                )
                patterns.append(pattern)
            
            return PatternSearchResult(
                patterns=patterns,
                total=len(patterns)
            )
        except Exception as e:
            log_manager.error(f"Error searching patterns: {e}")
            return PatternSearchResult(patterns=[], total=0)
    
    def match_patterns(self, input_text: str) -> List[PatternMatch]:
        """Match patterns against input text."""
        # This would need to be implemented to work with the database patterns
        # For now, we'll return an empty list
        log_manager.warning("Pattern matching not yet implemented for database service")
        return []
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        try:
            db_patterns = self.db_manager.get_all_patterns()
            categories = set()
            for pattern in db_patterns:
                if pattern.category is not None:
                    categories.add(str(pattern.category))
            
            return sorted(list(categories))
        except Exception as e:
            log_manager.error(f"Error getting categories: {e}")
            return []
    
    def get_vendors(self) -> List[str]:
        """Get all available vendors."""
        try:
            db_patterns = self.db_manager.get_all_patterns()
            vendors = set()
            for pattern in db_patterns:
                if pattern.vendor is not None:
                    vendors.add(str(pattern.vendor))
            
            return sorted(list(vendors))
        except Exception as e:
            log_manager.error(f"Error getting vendors: {e}")
            return []
    
    def get_statistics(self) -> CategoryStats:
        """Get database statistics."""
        try:
            db_patterns = self.db_manager.get_all_patterns()
            total_patterns = len(db_patterns)
            
            # Count by category
            category_counts = {}
            for pattern in db_patterns:
                category = str(pattern.category) if pattern.category is not None else 'unknown'
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by subcategory
            subcategory_counts = {}
            for pattern in db_patterns:
                subcategory = str(pattern.subcategory) if pattern.subcategory is not None else 'unknown'
                subcategory_counts[subcategory] = subcategory_counts.get(subcategory, 0) + 1
            
            stats = CategoryStats(
                total_patterns=total_patterns,
                categories=category_counts,
                subcategories=subcategory_counts
            )
            
            return stats
        except Exception as e:
            log_manager.error(f"Error getting statistics: {e}")
            return CategoryStats()

# Global database pattern service instance
db_pattern_service = DatabasePatternService()