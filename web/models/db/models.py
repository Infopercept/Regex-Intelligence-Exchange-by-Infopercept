"""
Database models for Regex Intelligence Exchange.
Only imported when SQLAlchemy is available.
"""

# This file should only be imported when SQLAlchemy is available
# The import statements are kept here but the file should only be imported conditionally

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

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