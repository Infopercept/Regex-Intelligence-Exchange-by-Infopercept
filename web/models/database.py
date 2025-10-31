"""
Database models for Regex Intelligence Exchange.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class PatternModel(Base):
    """Database model for technology patterns."""
    __tablename__ = 'patterns'
    
    id = Column(Integer, primary_key=True)
    vendor = Column(String(255), nullable=False)
    vendor_id = Column(String(255), nullable=False)
    product = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to pattern versions
    versions = relationship("PatternVersionModel", back_populates="pattern")
    
    # Index for faster queries
    __table_args__ = (
        Index('idx_vendor_id', 'vendor_id'),
        Index('idx_product_id', 'product_id'),
        Index('idx_category', 'category'),
        Index('idx_vendor_product', 'vendor_id', 'product_id', unique=True),
    )

class PatternVersionModel(Base):
    """Database model for pattern versions."""
    __tablename__ = 'pattern_versions'
    
    id = Column(Integer, primary_key=True)
    pattern_id = Column(Integer, ForeignKey('patterns.id'), nullable=False)
    version_range = Column(String(100), nullable=True)  # For version-specific patterns
    name = Column(String(255), nullable=False)
    pattern = Column(Text, nullable=False)
    version_group = Column(Integer, default=0)
    priority = Column(Integer, default=0)
    confidence = Column(Integer, default=0)  # Store as integer (0-100)
    metadata_json = Column(Text, nullable=True)  # Store metadata as JSON string
    pattern_type = Column(String(50), nullable=False, default='all_versions')  # 'all_versions' or 'version_specific'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to pattern
    pattern = relationship("PatternModel", back_populates="versions")
    
    # Index for faster queries
    __table_args__ = (
        Index('idx_pattern_id', 'pattern_id'),
        Index('idx_version_range', 'version_range'),
        Index('idx_pattern_type', 'pattern_type'),
    )

class DatabaseManager:
    """Manager for database operations."""
    
    def __init__(self, database_url='sqlite:///patterns.db'):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.Session()
    
    def save_pattern(self, pattern_data):
        """Save a pattern to the database."""
        session = self.get_session()
        try:
            # Check if pattern already exists
            existing_pattern = session.query(PatternModel).filter_by(
                vendor_id=pattern_data['vendor_id'],
                product_id=pattern_data['product_id']
            ).first()
            
            if existing_pattern:
                # Update existing pattern
                existing_pattern.vendor = pattern_data['vendor']
                existing_pattern.product = pattern_data['product']
                existing_pattern.category = pattern_data['category']
                existing_pattern.subcategory = pattern_data['subcategory']
                # updated_at will be automatically updated by SQLAlchemy due to onupdate=datetime.utcnow
                pattern_obj = existing_pattern
            else:
                # Create new pattern
                pattern_obj = PatternModel(
                    vendor=pattern_data['vendor'],
                    vendor_id=pattern_data['vendor_id'],
                    product=pattern_data['product'],
                    product_id=pattern_data['product_id'],
                    category=pattern_data['category'],
                    subcategory=pattern_data['subcategory']
                )
                session.add(pattern_obj)
                session.flush()  # Get the ID
            
            # Remove existing versions for this pattern
            session.query(PatternVersionModel).filter_by(pattern_id=pattern_obj.id).delete()
            
            # Save all_versions patterns
            if 'all_versions' in pattern_data:
                for version_pattern in pattern_data['all_versions']:
                    pattern_version = PatternVersionModel(
                        pattern_id=pattern_obj.id,
                        name=version_pattern['name'],
                        pattern=version_pattern['pattern'],
                        version_group=version_pattern.get('version_group', 0),
                        priority=version_pattern.get('priority', 0),
                        confidence=int(version_pattern.get('confidence', 0) * 100),
                        metadata_json=json.dumps(version_pattern.get('metadata', {})),
                        pattern_type='all_versions'
                    )
                    session.add(pattern_version)
            
            # Save version-specific patterns
            if 'versions' in pattern_data:
                for version_range, version_patterns in pattern_data['versions'].items():
                    for version_pattern in version_patterns:
                        pattern_version = PatternVersionModel(
                            pattern_id=pattern_obj.id,
                            version_range=version_range,
                            name=version_pattern['name'],
                            pattern=version_pattern['pattern'],
                            version_group=version_pattern.get('version_group', 0),
                            priority=version_pattern.get('priority', 0),
                            confidence=int(version_pattern.get('confidence', 0) * 100),
                            metadata_json=json.dumps(version_pattern.get('metadata', {})),
                            pattern_type='version_specific'
                        )
                        session.add(pattern_version)
            
            session.commit()
            return pattern_obj.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_pattern_by_id(self, vendor_id, product_id):
        """Get a pattern by vendor and product ID."""
        session = self.get_session()
        try:
            pattern = session.query(PatternModel).filter_by(
                vendor_id=vendor_id,
                product_id=product_id
            ).first()
            return pattern
        finally:
            session.close()
    
    def get_all_patterns(self):
        """Get all patterns."""
        session = self.get_session()
        try:
            patterns = session.query(PatternModel).all()
            return patterns
        finally:
            session.close()
    
    def search_patterns(self, query=None, category=None, vendor=None):
        """Search patterns with optional filtering."""
        session = self.get_session()
        try:
            query_obj = session.query(PatternModel)
            
            if category:
                query_obj = query_obj.filter(PatternModel.category == category)
            
            if vendor:
                query_obj = query_obj.filter(PatternModel.vendor.ilike(f'%{vendor}%'))
            
            if query:
                query_obj = query_obj.filter(
                    (PatternModel.vendor.ilike(f'%{query}%')) |
                    (PatternModel.product.ilike(f'%{query}%')) |
                    (PatternModel.category.ilike(f'%{query}%')) |
                    (PatternModel.subcategory.ilike(f'%{query}%'))
                )
            
            patterns = query_obj.all()
            return patterns
        finally:
            session.close()