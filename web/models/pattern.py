"""
Pattern data models for Regex Intelligence Exchange.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class PatternMetadata:
    """Metadata for a pattern."""
    author: str = ""
    created_at: str = ""
    updated_at: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    source: str = ""
    license: str = ""
    severity: str = ""
    cvss_score: float = 0.0
    cwe_ids: List[str] = field(default_factory=list)
    affected_versions: List[str] = field(default_factory=list)
    remediation: str = ""
    compiled_pattern: bool = False
    references: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class PatternVersion:
    """Version-specific pattern information."""
    name: str = ""
    pattern: str = ""
    version_group: int = 0
    priority: int = 0
    confidence: float = 0.0
    metadata: PatternMetadata = field(default_factory=PatternMetadata)

@dataclass
class Pattern:
    """Main pattern data model."""
    vendor: str = ""
    vendor_id: str = ""
    product: str = ""
    product_id: str = ""
    category: str = ""
    subcategory: str = ""
    versions: Dict[str, List[PatternVersion]] = field(default_factory=dict)
    all_versions: List[PatternVersion] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create a Pattern instance from a dictionary."""
        pattern = cls()
        pattern.vendor = data.get('vendor', '')
        pattern.vendor_id = data.get('vendor_id', '')
        pattern.product = data.get('product', '')
        pattern.product_id = data.get('product_id', '')
        pattern.category = data.get('category', '')
        pattern.subcategory = data.get('subcategory', '')
        
        # Parse versions
        if 'versions' in data:
            pattern.versions = {}
            for version, patterns in data['versions'].items():
                pattern.versions[version] = [
                    PatternVersion(
                        name=p.get('name', ''),
                        pattern=p.get('pattern', ''),
                        version_group=p.get('version_group', 0),
                        priority=p.get('priority', 0),
                        confidence=p.get('confidence', 0.0),
                        metadata=PatternMetadata(**p.get('metadata', {}))
                    ) for p in patterns
                ]
        
        # Parse all_versions
        if 'all_versions' in data:
            pattern.all_versions = [
                PatternVersion(
                    name=p.get('name', ''),
                    pattern=p.get('pattern', ''),
                    version_group=p.get('version_group', 0),
                    priority=p.get('priority', 0),
                    confidence=p.get('confidence', 0.0),
                    metadata=PatternMetadata(**p.get('metadata', {}))
                ) for p in data['all_versions']
            ]
        
        return pattern
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the Pattern instance to a dictionary."""
        return {
            'vendor': self.vendor,
            'vendor_id': self.vendor_id,
            'product': self.product,
            'product_id': self.product_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'versions': {
                version: [
                    {
                        'name': p.name,
                        'pattern': p.pattern,
                        'version_group': p.version_group,
                        'priority': p.priority,
                        'confidence': p.confidence,
                        'metadata': {
                            'author': p.metadata.author,
                            'created_at': p.metadata.created_at,
                            'updated_at': p.metadata.updated_at,
                            'description': p.metadata.description,
                            'tags': p.metadata.tags,
                            'test_cases': p.metadata.test_cases,
                            'source': p.metadata.source,
                            'license': p.metadata.license,
                            'severity': p.metadata.severity,
                            'cvss_score': p.metadata.cvss_score,
                            'cwe_ids': p.metadata.cwe_ids,
                            'affected_versions': p.metadata.affected_versions,
                            'remediation': p.metadata.remediation,
                            'compiled_pattern': p.metadata.compiled_pattern,
                            'references': p.metadata.references
                        }
                    } for p in patterns
                ] for version, patterns in self.versions.items()
            },
            'all_versions': [
                {
                    'name': p.name,
                    'pattern': p.pattern,
                    'version_group': p.version_group,
                    'priority': p.priority,
                    'confidence': p.confidence,
                    'metadata': {
                        'author': p.metadata.author,
                        'created_at': p.metadata.created_at,
                        'updated_at': p.metadata.updated_at,
                        'description': p.metadata.description,
                        'tags': p.metadata.tags,
                        'test_cases': p.metadata.test_cases,
                        'source': p.metadata.source,
                        'license': p.metadata.license,
                        'severity': p.metadata.severity,
                        'cvss_score': p.metadata.cvss_score,
                        'cwe_ids': p.metadata.cwe_ids,
                        'affected_versions': p.metadata.affected_versions,
                        'remediation': p.metadata.remediation,
                        'compiled_pattern': p.metadata.compiled_pattern,
                        'references': p.metadata.references
                    }
                } for p in self.all_versions
            ]
        }
    
    def get_pattern_count(self) -> int:
        """Get the total number of patterns."""
        count = len(self.all_versions)
        for patterns in self.versions.values():
            count += len(patterns)
        return count
    
    def get_safe_dict(self) -> Dict[str, Any]:
        """Get a dictionary representation without sensitive information."""
        return {
            'vendor': self.vendor,
            'vendor_id': self.vendor_id,
            'product': self.product,
            'product_id': self.product_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'pattern_count': self.get_pattern_count()
        }

@dataclass
class PatternSearchResult:
    """Search result for patterns."""
    patterns: List[Pattern] = field(default_factory=list)
    total: int = 0
    offset: int = 0
    limit: Optional[int] = None

@dataclass
class PatternMatch:
    """Result of pattern matching."""
    vendor: str = ""
    product: str = ""
    vendor_id: str = ""
    product_id: str = ""
    pattern_name: str = ""
    matched_text: str = ""
    version: Optional[str] = None
    version_range: Optional[str] = None

@dataclass
class CategoryStats:
    """Statistics for categories."""
    total_patterns: int = 0
    categories: Dict[str, int] = field(default_factory=dict)
    subcategories: Dict[str, int] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())