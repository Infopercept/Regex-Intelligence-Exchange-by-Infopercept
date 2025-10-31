#!/usr/bin/env python3
"""
Pattern Composition for Regex Intelligence Exchange
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path


class PatternComposer:
    """Compose complex patterns from simpler ones."""
    
    def __init__(self, patterns_dir="patterns/by-vendor"):
        self.patterns = {}
        self.load_patterns(patterns_dir)
    
    def load_patterns(self, patterns_dir):
        """Load all patterns into memory."""
        print("Loading patterns for composition...")
        pattern_count = 0
        
        for root, dirs, files in os.walk(patterns_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            pattern_data = json.load(f)
                        
                        vendor_id = pattern_data.get('vendor_id', 'unknown')
                        product_id = pattern_data.get('product_id', 'unknown')
                        pattern_key = f"{vendor_id}_{product_id}"
                        
                        self.patterns[pattern_key] = pattern_data
                        pattern_count += 1
                    
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {pattern_count} patterns for composition")
    
    def get_pattern(self, vendor_id, product_id):
        """Get a pattern by vendor and product ID."""
        pattern_key = f"{vendor_id}_{product_id}"
        return self.patterns.get(pattern_key)
    
    def compose_patterns(self, pattern_refs, composition_type="and"):
        """Compose multiple patterns into a single complex pattern.
        
        Args:
            pattern_refs: List of pattern references [{"vendor_id": "...", "product_id": "..."}, ...]
            composition_type: "and", "or", or "sequence"
        """
        if not pattern_refs:
            return None
        
        # Get the actual patterns
        patterns = []
        for ref in pattern_refs:
            pattern = self.get_pattern(ref['vendor_id'], ref['product_id'])
            if pattern:
                patterns.append(pattern)
            else:
                print(f"Warning: Pattern {ref['vendor_id']}/{ref['product_id']} not found")
        
        if not patterns:
            return None
        
        # Create composed pattern
        composed = {
            "vendor": "Composed Pattern",
            "vendor_id": "composed",
            "product": f"Composed_{composition_type}_Pattern",
            "product_id": f"composed-{composition_type}-pattern",
            "category": "composed",
            "subcategory": "pattern-composition",
            "composition": {
                "type": composition_type,
                "patterns": pattern_refs
            },
            "versions": {},
            "all_versions": []
        }
        
        # Generate composed patterns based on composition type
        if composition_type == "and":
            composed['all_versions'] = self._compose_and_patterns(patterns)
        elif composition_type == "or":
            composed['all_versions'] = self._compose_or_patterns(patterns)
        elif composition_type == "sequence":
            composed['all_versions'] = self._compose_sequence_patterns(patterns)
        
        return composed
    
    def _compose_and_patterns(self, patterns):
        """Compose patterns that must all match (AND logic)."""
        composed_patterns = []
        
        # For AND composition, we create patterns that look for combinations
        # This is a simplified approach - in practice, this would be more complex
        for i, pattern in enumerate(patterns):
            if 'all_versions' in pattern:
                for orig_pattern in pattern['all_versions']:
                    # Create a modified pattern with higher priority
                    composed_pattern = orig_pattern.copy()
                    composed_pattern['name'] = f"Composed AND: {orig_pattern.get('name', 'Unknown')}"
                    composed_pattern['priority'] = min(200, orig_pattern.get('priority', 100) + 20)
                    composed_pattern['confidence'] = min(1.0, orig_pattern.get('confidence', 0.8) + 0.1)
                    
                    # Add composition metadata
                    if 'metadata' not in composed_pattern:
                        composed_pattern['metadata'] = {}
                    
                    composed_pattern['metadata']['composition_type'] = 'and'
                    composed_pattern['metadata']['description'] = f"Part of AND composition with {len(patterns)} patterns"
                    
                    composed_patterns.append(composed_pattern)
        
        return composed_patterns
    
    def _compose_or_patterns(self, patterns):
        """Compose patterns where any can match (OR logic)."""
        composed_patterns = []
        
        # For OR composition, we combine similar patterns
        all_orig_patterns = []
        for pattern in patterns:
            if 'all_versions' in pattern:
                all_orig_patterns.extend(pattern['all_versions'])
        
        # Group similar patterns by purpose
        pattern_groups = {}
        for orig_pattern in all_orig_patterns:
            # Group by category or purpose
            purpose = orig_pattern.get('name', 'unknown').split()[0]  # First word as category
            if purpose not in pattern_groups:
                pattern_groups[purpose] = []
            pattern_groups[purpose].append(orig_pattern)
        
        # Create OR patterns for each group
        for purpose, group_patterns in pattern_groups.items():
            if len(group_patterns) > 1:
                # Create a combined regex pattern
                regex_parts = [p['pattern'] for p in group_patterns]
                combined_pattern = f"({'|'.join(regex_parts)})"
                
                composed_pattern = {
                    "name": f"Composed OR: {purpose} Detection",
                    "pattern": combined_pattern,
                    "version_group": 1,  # Simplified
                    "priority": max(p.get('priority', 100) for p in group_patterns),
                    "confidence": max(p.get('confidence', 0.8) for p in group_patterns),
                    "metadata": {
                        "author": "Pattern Composer",
                        "created_at": datetime.now().strftime("%Y-%m-%d"),
                        "updated_at": datetime.now().strftime("%Y-%m-%d"),
                        "description": f"OR composition of {len(group_patterns)} {purpose} patterns",
                        "tags": ["composed", "or-composition", purpose.lower()],
                        "composition_type": "or"
                    }
                }
                composed_patterns.append(composed_pattern)
            else:
                # Just use the single pattern
                composed_patterns.extend(group_patterns)
        
        return composed_patterns
    
    def _compose_sequence_patterns(self, patterns):
        """Compose patterns that must match in sequence."""
        composed_patterns = []
        
        # For sequence composition, we create patterns that look for ordered matches
        # This is a conceptual implementation
        if len(patterns) >= 2:
            first_pattern = patterns[0]
            last_pattern = patterns[-1]
            
            # Create a pattern that represents the sequence
            composed_pattern = {
                "name": "Composed Sequence Pattern",
                "pattern": f"{first_pattern.get('vendor', 'First')}.*{last_pattern.get('vendor', 'Last')}",
                "version_group": 0,
                "priority": 150,
                "confidence": 0.9,
                "metadata": {
                    "author": "Pattern Composer",
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                    "description": f"Sequence composition of {len(patterns)} patterns",
                    "tags": ["composed", "sequence-composition"],
                    "composition_type": "sequence",
                    "sequence_steps": len(patterns)
                }
            }
            composed_patterns.append(composed_pattern)
        
        return composed_patterns
    
    def save_composed_pattern(self, composed_pattern, output_dir="composed-patterns"):
        """Save a composed pattern to file."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create filename
        filename = f"{composed_pattern['vendor_id']}_{composed_pattern['product_id']}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save pattern
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(composed_pattern, f, indent=2, ensure_ascii=False)
        
        print(f"Composed pattern saved to: {filepath}")
        return filepath


def demo_pattern_composition():
    """Demonstrate pattern composition capabilities."""
    print("Pattern Composition Demo")
    print("=" * 30)
    
    # Create composer
    composer = PatternComposer()
    
    # Example: Compose Apache and PHP patterns (AND composition)
    print("\n1. AND Composition Example:")
    and_patterns = [
        {"vendor_id": "apache", "product_id": "apache-httpd"},
        {"vendor_id": "php", "product_id": "php"}
    ]
    
    and_composed = composer.compose_patterns(and_patterns, "and")
    if and_composed:
        print(f"   Composed {len(and_composed['all_versions'])} AND patterns")
        composer.save_composed_pattern(and_composed)
    
    # Example: Compose different web server patterns (OR composition)
    print("\n2. OR Composition Example:")
    or_patterns = [
        {"vendor_id": "apache", "product_id": "apache-httpd"},
        {"vendor_id": "nginx", "product_id": "nginx"}
    ]
    
    or_composed = composer.compose_patterns(or_patterns, "or")
    if or_composed:
        print(f"   Composed {len(or_composed['all_versions'])} OR patterns")
        composer.save_composed_pattern(or_composed)
    
    # Example: Compose sequence patterns
    print("\n3. Sequence Composition Example:")
    sequence_patterns = [
        {"vendor_id": "apache", "product_id": "apache-httpd"},
        {"vendor_id": "php", "product_id": "php"}
    ]
    
    sequence_composed = composer.compose_patterns(sequence_patterns, "sequence")
    if sequence_composed:
        print(f"   Composed {len(sequence_composed['all_versions'])} sequence patterns")
        composer.save_composed_pattern(sequence_composed)
    
    print("\nPattern composition demo completed")


def main():
    """Main function."""
    print("Pattern Composition for Regex Intelligence Exchange")
    print("=" * 50)
    
    demo_pattern_composition()


if __name__ == "__main__":
    main()