"""
Database models for Regex Intelligence Exchange.
"""

# Global flag to track database availability
DATABASE_AVAILABLE = False

# Try to import database components, but make it optional
try:
    from .db.models import PatternModel as _DB_PatternModel, PatternVersionModel as _DB_PatternVersionModel
    from .db.manager import DatabaseManager as _DB_DatabaseManager
    DATABASE_AVAILABLE = True
    
    # Export the classes
    PatternModel = _DB_PatternModel
    PatternVersionModel = _DB_PatternVersionModel
    DatabaseManager = _DB_DatabaseManager
except ImportError:
    # Provide dummy implementations when database is not available
    class PatternModel:
        pass
    
    class PatternVersionModel:
        pass
    
    class DatabaseManager:
        def __init__(self, database_url='sqlite:///patterns.db'):
            self.engine = None
            self.Session = None
        
        def get_session(self):
            return None
        
        def save_pattern(self, pattern_data):
            return None
        
        def get_pattern_by_id(self, vendor_id, product_id):
            return None
        
        def get_all_patterns(self):
            return []
        
        def search_patterns(self, query=None, category=None, vendor=None):
            return []