"""
Database-based pattern service for Regex Intelligence Exchange.
"""

import os
import json
from typing import List, Optional
from models.pattern import Pattern
from utils.logging import log_manager

# Try to import database components, but make it optional
DATABASE_AVAILABLE = False
DatabaseManager = None

try:
    from models.database import DatabaseManager as _DatabaseManager, PatternModel
    DatabaseManager = _DatabaseManager
    DATABASE_AVAILABLE = True
except ImportError:
    log_manager.warning("Database components not available, using file-based storage only")

class DatabasePatternService:
    """Service for managing patterns stored in a database."""
    
    def __init__(self, database_url: str = 'sqlite:///patterns.db'):
        if not DATABASE_AVAILABLE:
            raise ImportError("Database components not available")
            
        self.db_manager = DatabaseManager(database_url) if DatabaseManager else None
        log_manager.info("Database pattern service initialized")
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns from the database."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return []
            
        try:
            db_patterns = self.db_manager.get_all_patterns()
            patterns = []
            
            for db_pattern in db_patterns:
                # Convert database pattern to our Pattern model
                pattern = Pattern(
                    vendor=db_pattern.vendor,
                    vendor_id=db_pattern.vendor_id,
                    product=db_pattern.product,
                    product_id=db_pattern.product_id,
                    category=db_pattern.category,
                    subcategory=db_pattern.subcategory or '',
                    versions={},  # This would need to be populated from PatternVersionModel
                    all_versions=[]  # This would need to be populated from PatternVersionModel
                )
                patterns.append(pattern)
            
            return patterns
        except Exception as e:
            log_manager.error(f"Error getting patterns from database: {e}")
            return []
    
    def get_pattern_by_id(self, vendor_id: str, product_id: str) -> Optional[Pattern]:
        """Get a specific pattern by vendor and product ID."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return None
            
        try:
            db_pattern = self.db_manager.get_pattern_by_id(vendor_id, product_id)
            if not db_pattern:
                return None
            
            # Convert database pattern to our Pattern model
            pattern = Pattern(
                vendor=db_pattern.vendor,
                vendor_id=db_pattern.vendor_id,
                product=db_pattern.product,
                product_id=db_pattern.product_id,
                category=db_pattern.category,
                subcategory=db_pattern.subcategory or '',
                versions={},  # This would need to be populated from PatternVersionModel
                all_versions=[]  # This would need to be populated from PatternVersionModel
            )
            
            return pattern
        except Exception as e:
            log_manager.error(f"Error getting pattern from database: {e}")
            return None
    
    def search_patterns(self, query: str = '', category: str = '', vendor: str = '') -> List[Pattern]:
        """Search patterns in the database."""
        if not DATABASE_AVAILABLE or not self.db_manager:
            return []
            
        try:
            db_patterns = self.db_manager.search_patterns(query, category, vendor)
            patterns = []
            
            for db_pattern in db_patterns:
                # Convert database pattern to our Pattern model
                pattern = Pattern(
                    vendor=db_pattern.vendor,
                    vendor_id=db_pattern.vendor_id,
                    product=db_pattern.product,
                    product_id=db_pattern.product_id,
                    category=db_pattern.category,
                    subcategory=db_pattern.subcategory or '',
                    versions={},  # This would need to be populated from PatternVersionModel
                    all_versions=[]  # This would need to be populated from PatternVersionModel
                )
                patterns.append(pattern)
            
            return patterns
        except Exception as e:
            log_manager.error(f"Error searching patterns in database: {e}")
            return []
    
    def get_statistics(self):
        """Get pattern statistics."""
        # Define Stats class only once
        class Stats:
            def __init__(self, total_patterns=0, categories=None, subcategories=None):
                self.total_patterns = total_patterns
                self.categories = categories or {}
                self.subcategories = subcategories or {}
        
        if not DATABASE_AVAILABLE or not self.db_manager:
            # Return a dummy statistics object
            return Stats()
            
        try:
            db_patterns = self.db_manager.get_all_patterns()
            
            # Calculate statistics
            categories = {}
            subcategories = {}
            
            for pattern in db_patterns:
                # Count categories
                if pattern.category in categories:
                    categories[pattern.category] += 1
                else:
                    categories[pattern.category] = 1
                
                # Count subcategories
                if pattern.subcategory:
                    if pattern.subcategory in subcategories:
                        subcategories[pattern.subcategory] += 1
                    else:
                        subcategories[pattern.subcategory] = 1
            
            return Stats(len(db_patterns), categories, subcategories)
        except Exception as e:
            log_manager.error(f"Error getting database statistics: {e}")
            # Return dummy statistics
            return Stats()