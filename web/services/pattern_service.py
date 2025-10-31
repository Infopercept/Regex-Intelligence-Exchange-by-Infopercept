"""
Pattern service for Regex Intelligence Exchange.
Supports both file-based and database-based pattern storage.
"""

import os
import json
import glob
from typing import List, Optional
from models.pattern import Pattern, PatternSearchResult
from utils.logging import log_manager

# Try to import database service, but make it optional
DATABASE_SERVICE_AVAILABLE = False
DatabasePatternService = None

try:
    import sqlalchemy
    # Try to import database service
    from services.db_pattern_service import DatabasePatternService as _DatabasePatternService
    DatabasePatternService = _DatabasePatternService
    DATABASE_SERVICE_AVAILABLE = True
except ImportError:
    log_manager.warning("Database pattern service not available, using file-based storage only")

class PatternService:
    """Service for managing technology fingerprinting patterns."""
    
    def __init__(self, patterns_dir: Optional[str] = None, use_database: bool = False):
        # Determine if we should use database (only if available and requested)
        self.use_database = use_database and DATABASE_SERVICE_AVAILABLE and os.environ.get('USE_DATABASE', 'false').lower() == 'true'
        
        if self.use_database and DatabasePatternService:
            try:
                # Use database service
                database_url = os.environ.get('DATABASE_URL', 'sqlite:///patterns.db')
                self.db_service = DatabasePatternService(database_url)
                log_manager.info("Using database pattern service")
            except Exception as e:
                log_manager.error(f"Failed to initialize database service: {e}")
                self.use_database = False
                self.db_service = None
        else:
            self.db_service = None
        
        # Fall back to file-based service
        if not self.use_database:
            self.patterns_dir = patterns_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'patterns', 'by-vendor')
            self.patterns = {}
            self.stats = None
            self.load_patterns()
            log_manager.info("Using file-based pattern service")
    
    def load_patterns(self):
        """Load all patterns from the file system."""
        if self.use_database:
            return  # Don't load file patterns if using database
            
        self.patterns = {}
        pattern_files = glob.glob(os.path.join(self.patterns_dir, '**', '*.json'), recursive=True)
        
        for pattern_file in pattern_files:
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                
                # Create pattern object
                pattern = Pattern.from_dict(pattern_data)
                
                # Store pattern by vendor_id/product_id
                pattern_key = f"{pattern.vendor_id}/{pattern.product_id}"
                self.patterns[pattern_key] = pattern
            except Exception as e:
                log_manager.error(f"Error loading pattern from {pattern_file}: {e}")
        
        log_manager.info(f"Loaded {len(self.patterns)} patterns from file system")
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all patterns."""
        if self.use_database and self.db_service:
            return self.db_service.get_all_patterns()
        else:
            return list(self.patterns.values())
    
    def get_pattern_by_id(self, vendor_id: str, product_id: str) -> Optional[Pattern]:
        """Get a specific pattern by vendor and product ID."""
        if self.use_database and self.db_service:
            return self.db_service.get_pattern_by_id(vendor_id, product_id)
        else:
            pattern_key = f"{vendor_id}/{product_id}"
            return self.patterns.get(pattern_key)
    
    def search_patterns(self, query: str = '', category: str = '', vendor: str = '') -> PatternSearchResult:
        """Search patterns with optional filtering."""
        if self.use_database and self.db_service:
            patterns = self.db_service.search_patterns(query, category, vendor)
        else:
            patterns = list(self.patterns.values())
            
            # Apply filters
            if category:
                patterns = [p for p in patterns if p.category.lower() == category.lower()]
            
            if vendor:
                patterns = [p for p in patterns if vendor.lower() in p.vendor.lower()]
            
            if query:
                query_lower = query.lower()
                patterns = [p for p in patterns if (
                    query_lower in p.vendor.lower() or
                    query_lower in p.product.lower() or
                    query_lower in p.category.lower() or
                    (p.subcategory and query_lower in p.subcategory.lower())
                )]
        
        # Create search result
        result = PatternSearchResult()
        result.patterns = patterns
        result.total = len(patterns)
        result.limit = None
        
        return result
    
    def match_patterns(self, text: str) -> List:
        """Match patterns against input text."""
        # This method would use the pattern matching logic
        # For now, we'll return an empty list as the implementation
        # is in the pattern_matcher module
        return []
    
    def get_statistics(self):
        """Get pattern statistics."""
        if self.use_database and self.db_service:
            return self.db_service.get_statistics()
        else:
            if not self.stats:
                # Calculate statistics from file patterns
                categories = {}
                subcategories = {}
                
                for pattern in self.patterns.values():
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
                
                # Create statistics object
                class Stats:
                    def __init__(self, total_patterns, categories, subcategories):
                        self.total_patterns = total_patterns
                        self.categories = categories
                        self.subcategories = subcategories
                
                self.stats = Stats(len(self.patterns), categories, subcategories)
            
            return self.stats

# Global pattern service instance
pattern_service = PatternService()