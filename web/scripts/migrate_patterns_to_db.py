#!/usr/bin/env python3
"""
Migration script to move patterns from file system to database.
"""

import os
import sys
import json
from pathlib import Path
from models.database import DatabaseManager

def migrate_patterns(patterns_dir, db_manager):
    """Migrate patterns from file system to database."""
    print(f"Starting migration of patterns from {patterns_dir}")
    
    # Counters
    total_files = 0
    migrated_files = 0
    error_files = 0
    
    # Walk through the patterns directory
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    # Load pattern from file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pattern_data = json.load(f)
                    
                    # Save to database
                    db_manager.save_pattern(pattern_data)
                    migrated_files += 1
                    
                    # Print progress
                    if total_files % 100 == 0:
                        print(f"Processed {total_files} files...")
                        
                except Exception as e:
                    print(f"Error migrating {file_path}: {e}")
                    error_files += 1
    
    print(f"Migration completed!")
    print(f"Total files processed: {total_files}")
    print(f"Successfully migrated: {migrated_files}")
    print(f"Errors: {error_files}")

def main():
    """Main function."""
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Get patterns directory
    patterns_dir = os.path.join(project_root, 'patterns', 'by-vendor')
    
    # Initialize database manager
    # For production, you would use a proper database URL
    db_manager = DatabaseManager('sqlite:///patterns.db')
    
    # Migrate patterns
    migrate_patterns(patterns_dir, db_manager)

if __name__ == '__main__':
    main()