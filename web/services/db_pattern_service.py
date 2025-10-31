"""
Database-based pattern service for Regex Intelligence Exchange.
"""

import os
import json
from typing import List, Optional
from models.pattern import Pattern
from utils.logging import log_manager

# Database service is only available if SQLAlchemy is installed
DATABASE_SERVICE_AVAILABLE = False
DatabaseManager = None

# Try to import SQLAlchemy and database components, but make it completely optional
# We do this inside a function to avoid module-level import issues
def init_database_components():
    global DATABASE_SERVICE_AVAILABLE, DatabaseManager
    try:
        import sqlalchemy
        # Try to import our database models
        from models.database import DatabaseManager as _DatabaseManager, PatternModel
        DatabaseManager = _DatabaseManager
        DATABASE_SERVICE_AVAILABLE = True
        log_manager.info("Database components available")
        return True
    except ImportError as e:
        log_manager.warning(f"Database components not available, using file-based storage only: {e}")
        return False
    except Exception as e:
        log_manager.warning(f"Database components not available due to error, using file-based storage only: {e}")
        return False

# Initialize database components
init_database_components()

class DatabasePatternService:
    """Service for managing patterns stored in a database."""
    
    def __init__(self, database_url: str = 'sqlite:///patterns.db'):
        self.db_manager = None
        if DATABASE_SERVICE_AVAILABLE and DatabaseManager:
            try:
                self.db_manager = DatabaseManager(database_url)
                log_manager.info("Database pattern service initialized")
            except Exception as e:
                log_manager.error(f"Failed to initialize database service: {e}")
                self.db_manager = None
        else:
            log_manager.warning("Database service not available")
    
    def is_available(self) -> bool:
        """Check if database service is available and properly initialized."""
        return self.db_manager is not None
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns from the database."""
        if not self.is_available() or self.db_manager is None:
            return []
            
        try:
            db_patterns = self.db_manager.get_all_patterns()
            patterns = []
            
            for db_pattern in db_patterns:
                # Convert database pattern to our Pattern model
                pattern = Pattern(
                    vendor=getattr(db_pattern, 'vendor', ''),
                    vendor_id=getattr(db_pattern, 'vendor_id', ''),
                    product=getattr(db_pattern, 'product', ''),
                    product_id=getattr(db_pattern, 'product_id', ''),
                    category=getattr(db_pattern, 'category', ''),
                    subcategory=getattr(db_pattern, 'subcategory', '') or '',
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
        if not self.is_available() or self.db_manager is None:
            return None
            
        try:
            db_pattern = self.db_manager.get_pattern_by_id(vendor_id, product_id)
            if not db_pattern:
                return None
            
            # Convert database pattern to our Pattern model
            pattern = Pattern(
                vendor=getattr(db_pattern, 'vendor', ''),
                vendor_id=getattr(db_pattern, 'vendor_id', ''),
                product=getattr(db_pattern, 'product', ''),
                product_id=getattr(db_pattern, 'product_id', ''),
                category=getattr(db_pattern, 'category', ''),
                subcategory=getattr(db_pattern, 'subcategory', '') or '',
                versions={},  # This would need to be populated from PatternVersionModel
                all_versions=[]  # This would need to be populated from PatternVersionModel
            )
            
            return pattern
        except Exception as e:
            log_manager.error(f"Error getting pattern from database: {e}")
            return None
    
    def search_patterns(self, query: str = '', category: str = '', vendor: str = '') -> List[Pattern]:
        """Search patterns in the database."""
        if not self.is_available() or self.db_manager is None:
            return []
            
        try:
            db_patterns = self.db_manager.search_patterns(query, category, vendor)
            patterns = []
            
            for db_pattern in db_patterns:
                # Convert database pattern to our Pattern model
                pattern = Pattern(
                    vendor=getattr(db_pattern, 'vendor', ''),
                    vendor_id=getattr(db_pattern, 'vendor_id', ''),
                    product=getattr(db_pattern, 'product', ''),
                    product_id=getattr(db_pattern, 'product_id', ''),
                    category=getattr(db_pattern, 'category', ''),
                    subcategory=getattr(db_pattern, 'subcategory', '') or '',
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
        
        if not self.is_available() or self.db_manager is None:
            # Return a dummy statistics object
            return Stats()
            
        try:
            db_patterns = self.db_manager.get_all_patterns()
            
            # Calculate statistics
            categories = {}
            subcategories = {}
            
            for pattern in db_patterns:
                # Count categories
                category = getattr(pattern, 'category', '')
                if category:
                    if category in categories:
                        categories[category] += 1
                    else:
                        categories[category] = 1
                
                # Count subcategories
                subcategory = getattr(pattern, 'subcategory', '')
                if subcategory:
                    if subcategory in subcategories:
                        subcategories[subcategory] += 1
                    else:
                        subcategories[subcategory] = 1
            
            return Stats(len(db_patterns), categories, subcategories)
        except Exception as e:
            log_manager.error(f"Error getting database statistics: {e}")
            # Return dummy statistics
            return Stats()