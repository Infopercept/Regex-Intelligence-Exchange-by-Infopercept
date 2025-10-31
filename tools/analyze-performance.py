#!/usr/bin/env python3
"""
Script to analyze performance bottlenecks and suggest optimizations
"""

import json
import os
import sys
import re
import time
from pathlib import Path
from collections import defaultdict, Counter


def analyze_pattern_complexity(pattern_str):
    """Analyze the complexity of a regex pattern."""
    complexity_score = 0
    
    # Count various regex elements that can impact performance
    complexity_score += len(re.findall(r'\*', pattern_str)) * 2  # Wildcards
    complexity_score += len(re.findall(r'\+', pattern_str)) * 2  # Plus quantifiers
    complexity_score += len(re.findall(r'\{', pattern_str)) * 1  # Curly brace quantifiers
    complexity_score += len(re.findall(r'\(', pattern_str)) * 1  # Capture groups
    complexity_score += len(re.findall(r'\[', pattern_str)) * 1  # Character classes
    complexity_score += len(re.findall(r'\\', pattern_str)) * 1  # Escape sequences
    complexity_score += len(pattern_str) * 0.1  # Overall length
    
    return complexity_score


def find_performance_bottlenecks(patterns_dir):
    """Find patterns that may have performance issues."""
    bottlenecks = []
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Analyze all_versions patterns
                    if 'all_versions' in data:
                        for i, pattern in enumerate(data['all_versions']):
                            if 'pattern' in pattern:
                                complexity = analyze_pattern_complexity(pattern['pattern'])
                                if complexity > 10:  # Threshold for complex patterns
                                    bottlenecks.append({
                                        'file': file_path,
                                        'pattern_name': pattern.get('name', 'Unknown'),
                                        'pattern_str': pattern['pattern'],
                                        'complexity': complexity,
                                        'type': 'all_versions',
                                        'index': i
                                    })
                    
                    # Analyze version-specific patterns
                    if 'versions' in data:
                        for version, version_patterns in data['versions'].items():
                            for i, pattern in enumerate(version_patterns):
                                if 'pattern' in pattern:
                                    complexity = analyze_pattern_complexity(pattern['pattern'])
                                    if complexity > 10:  # Threshold for complex patterns
                                        bottlenecks.append({
                                            'file': file_path,
                                            'pattern_name': pattern.get('name', 'Unknown'),
                                            'pattern_str': pattern['pattern'],
                                            'complexity': complexity,
                                            'type': f'versions.{version}',
                                            'index': i
                                        })
                    
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
    
    # Sort by complexity (highest first)
    bottlenecks.sort(key=lambda x: x['complexity'], reverse=True)
    return bottlenecks


def benchmark_pattern_matching(pattern_str, test_inputs, iterations=1000):
    """Benchmark pattern matching performance."""
    try:
        pattern = re.compile(pattern_str)
    except re.error:
        return None
    
    start_time = time.time()
    for _ in range(iterations):
        for test_input in test_inputs:
            pattern.search(test_input)
    end_time = time.time()
    
    return (end_time - start_time) / iterations


def suggest_optimizations(bottlenecks, limit=10):
    """Suggest optimizations for complex patterns."""
    suggestions = []
    
    for bottleneck in bottlenecks[:limit]:
        suggestion = {
            'file': bottleneck['file'],
            'pattern_name': bottleneck['pattern_name'],
            'current_pattern': bottleneck['pattern_str'],
            'complexity': bottleneck['complexity']
        }
        
        # Suggest optimizations based on pattern characteristics
        pattern_str = bottleneck['pattern_str']
        
        suggestions_list = []
        
        # Look for common optimization opportunities
        if '\\s*' in pattern_str:
            suggestions_list.append("Replace \\s* with \\s+ if whitespace is required")
        
        if '\\w*' in pattern_str:
            suggestions_list.append("Replace \\w* with \\w+ if at least one word character is required")
        
        if '\\d*' in pattern_str:
            suggestions_list.append("Replace \\d* with \\d+ if at least one digit is required")
        
        if '{1,}' in pattern_str:
            suggestions_list.append("Replace {1,} with +")
        
        if '{0,1}' in pattern_str:
            suggestions_list.append("Replace {0,1} with ?")
        
        if '\\S*' in pattern_str:
            suggestions_list.append("Replace \\S* with \\S+ if at least one non-whitespace character is required")
        
        # Suggest reducing backtracking
        if '.*' in pattern_str or '.+' in pattern_str:
            suggestions_list.append("Consider using more specific character classes instead of . to reduce backtracking")
        
        # Suggest using non-capturing groups if not needed
        if '(?:' not in pattern_str and '(' in pattern_str and pattern_str.count('(') > pattern_str.count('(?:'):
            suggestions_list.append("Use non-capturing groups (?:...) if you don't need to capture the group")
        
        suggestion['suggestions'] = suggestions_list
        suggestions.append(suggestion)
    
    return suggestions


def generate_performance_report(patterns_dir):
    """Generate a comprehensive performance report."""
    print("Analyzing pattern performance...")
    
    # Find performance bottlenecks
    bottlenecks = find_performance_bottlenecks(patterns_dir)
    
    print(f"Found {len(bottlenecks)} potentially complex patterns")
    
    # Generate suggestions
    suggestions = suggest_optimizations(bottlenecks)
    
    # Create report
    report = {
        'total_patterns_analyzed': len(bottlenecks),
        'complex_patterns': len([b for b in bottlenecks if b['complexity'] > 15]),
        'high_complexity_patterns': len([b for b in bottlenecks if b['complexity'] > 20]),
        'optimization_suggestions': suggestions
    }
    
    return report


def main():
    """Main function."""
    if len(sys.argv) > 1:
        patterns_dir = sys.argv[1]
    else:
        patterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'patterns', 'by-vendor')
    
    if not os.path.exists(patterns_dir):
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)
    
    # Generate performance report
    report = generate_performance_report(patterns_dir)
    
    print("\n=== PERFORMANCE ANALYSIS REPORT ===")
    print(f"Total patterns analyzed: {report['total_patterns_analyzed']}")
    print(f"Complex patterns (>15): {report['complex_patterns']}")
    print(f"High complexity patterns (>20): {report['high_complexity_patterns']}")
    
    print("\n=== OPTIMIZATION SUGGESTIONS ===")
    for i, suggestion in enumerate(report['optimization_suggestions'], 1):
        print(f"\n{i}. {suggestion['pattern_name']}")
        print(f"   File: {suggestion['file']}")
        print(f"   Complexity Score: {suggestion['complexity']:.2f}")
        print(f"   Current Pattern: {suggestion['current_pattern']}")
        print("   Suggestions:")
        for j, s in enumerate(suggestion['suggestions'], 1):
            print(f"     {j}. {s}")


if __name__ == "__main__":
    main()