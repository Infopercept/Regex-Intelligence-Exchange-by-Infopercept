#!/usr/bin/env python3
"""
Advanced Analytics for Regex Intelligence Exchange
"""

import json
import os
import sys
import re
import statistics
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path


def analyze_pattern_complexity(pattern_str):
    """Analyze the complexity of a regex pattern."""
    metrics = {
        'length': len(pattern_str),
        'wildcards': len(re.findall(r'[*+?]', pattern_str)),
        'groups': len(re.findall(r'\(.*?\)', pattern_str)),
        'character_classes': len(re.findall(r'\[.*?\]', pattern_str)),
        'alternations': len(re.findall(r'\|', pattern_str)),
        'quantifiers': len(re.findall(r'{.*?}', pattern_str)),
        'escapes': len(re.findall(r'\\.', pattern_str))
    }
    
    # Calculate complexity score
    complexity_score = (
        metrics['length'] * 0.1 +
        metrics['wildcards'] * 2 +
        metrics['groups'] * 1.5 +
        metrics['character_classes'] * 1 +
        metrics['alternations'] * 1.5 +
        metrics['quantifiers'] * 1 +
        metrics['escapes'] * 0.5
    )
    
    metrics['complexity_score'] = int(round(complexity_score, 2))
    return metrics


def analyze_pattern_effectiveness(pattern_data, test_results=None):
    """Analyze the effectiveness of patterns."""
    effectiveness = {
        'total_patterns': 0,
        'patterns_with_tests': 0,
        'patterns_with_references': 0,
        'patterns_with_severity': 0,
        'patterns_with_cvss': 0,
        'avg_confidence': 0,
        'avg_priority': 0,
        'test_pass_rate': 0
    }
    
    confidences = []
    priorities = []
    test_results_list = []
    
    # Analyze all_versions patterns
    if 'all_versions' in pattern_data:
        for pattern in pattern_data['all_versions']:
            effectiveness['total_patterns'] += 1
            confidences.append(pattern.get('confidence', 0))
            priorities.append(pattern.get('priority', 0))
            
            if 'metadata' in pattern:
                metadata = pattern['metadata']
                if 'test_cases' in metadata:
                    effectiveness['patterns_with_tests'] += 1
                if 'references' in metadata:
                    effectiveness['patterns_with_references'] += 1
                if 'severity' in metadata:
                    effectiveness['patterns_with_severity'] += 1
                if 'cvss_score' in metadata:
                    effectiveness['patterns_with_cvss'] += 1
    
    # Analyze version-specific patterns
    if 'versions' in pattern_data:
        for version_patterns in pattern_data['versions'].values():
            for pattern in version_patterns:
                effectiveness['total_patterns'] += 1
                confidences.append(pattern.get('confidence', 0))
                priorities.append(pattern.get('priority', 0))
                
                if 'metadata' in pattern:
                    metadata = pattern['metadata']
                    if 'test_cases' in metadata:
                        effectiveness['patterns_with_tests'] += 1
                    if 'references' in metadata:
                        effectiveness['patterns_with_references'] += 1
                    if 'severity' in metadata:
                        effectiveness['patterns_with_severity'] += 1
                    if 'cvss_score' in metadata:
                        effectiveness['patterns_with_cvss'] += 1
    
    # Calculate averages
    if confidences:
        effectiveness['avg_confidence'] = int(round(statistics.mean(confidences), 2))
    if priorities:
        effectiveness['avg_priority'] = int(round(statistics.mean(priorities), 2))
    
    # Calculate test pass rate if test results provided
    if test_results:
        passed = sum(1 for result in test_results if result.get('passed', False))
        total = len(test_results)
        if total > 0:
            effectiveness['test_pass_rate'] = int(round((passed / total) * 100, 2))
    
    return effectiveness


def generate_comprehensive_report(patterns_dir="patterns/by-vendor", output_file="advanced-analytics-report.json"):
    """Generate a comprehensive analytics report."""
    print("Generating comprehensive analytics report...")
    
    # Initialize report data
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {},
        'pattern_statistics': {},
        'complexity_analysis': {},
        'effectiveness_analysis': {},
        'category_analysis': {},
        'vendor_analysis': {}
    }
    
    # Collect data from all patterns
    all_patterns = []
    complexity_scores = []
    effectiveness_scores = []
    category_counts = defaultdict(int)
    vendor_counts = defaultdict(int)
    pattern_metrics = []
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pattern_data = json.load(f)
                    
                    all_patterns.append(pattern_data)
                    
                    # Collect basic statistics
                    vendor = pattern_data.get('vendor', 'Unknown')
                    category = pattern_data.get('category', 'Unknown')
                    vendor_counts[vendor] += 1
                    category_counts[category] += 1
                    
                    # Analyze pattern complexity
                    if 'all_versions' in pattern_data:
                        for pattern in pattern_data['all_versions']:
                            if 'pattern' in pattern:
                                complexity = analyze_pattern_complexity(pattern['pattern'])
                                complexity_scores.append(complexity['complexity_score'])
                                pattern_metrics.append(complexity)
                    
                    if 'versions' in pattern_data:
                        for version_patterns in pattern_data['versions'].values():
                            for pattern in version_patterns:
                                if 'pattern' in pattern:
                                    complexity = analyze_pattern_complexity(pattern['pattern'])
                                    complexity_scores.append(complexity['complexity_score'])
                                    pattern_metrics.append(complexity)
                    
                    # Analyze pattern effectiveness
                    effectiveness = analyze_pattern_effectiveness(pattern_data)
                    effectiveness_scores.append(effectiveness['avg_confidence'])
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    # Generate summary statistics
    report['summary'] = {
        'total_patterns': len(all_patterns),
        'total_regex_patterns': len(pattern_metrics),
        'avg_complexity_score': int(round(statistics.mean(complexity_scores), 2)) if complexity_scores else 0,
        'median_complexity_score': int(round(statistics.median(complexity_scores), 2)) if complexity_scores else 0,
        'max_complexity_score': int(round(max(complexity_scores), 2)) if complexity_scores else 0,
        'min_complexity_score': int(round(min(complexity_scores), 2)) if complexity_scores else 0,
        'avg_effectiveness_score': int(round(statistics.mean(effectiveness_scores), 2)) if effectiveness_scores else 0,
        'categories': len(category_counts),
        'vendors': len(vendor_counts)
    }
    
    # Pattern statistics
    report['pattern_statistics'] = {
        'by_category': dict(category_counts),
        'by_vendor': dict(sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True)[:20]),  # Top 20 vendors
        'complexity_distribution': {
            'low': len([s for s in complexity_scores if s < 10]),
            'medium': len([s for s in complexity_scores if 10 <= s < 20]),
            'high': len([s for s in complexity_scores if s >= 20])
        }
    }
    
    # Complexity analysis
    if pattern_metrics:
        report['complexity_analysis'] = {
            'avg_length': int(round(statistics.mean([m['length'] for m in pattern_metrics]), 2)),
            'avg_wildcards': int(round(statistics.mean([m['wildcards'] for m in pattern_metrics]), 2)),
            'avg_groups': int(round(statistics.mean([m['groups'] for m in pattern_metrics]), 2)),
            'avg_character_classes': int(round(statistics.mean([m['character_classes'] for m in pattern_metrics]), 2)),
            'most_complex_patterns': sorted(pattern_metrics, key=lambda x: x['complexity_score'], reverse=True)[:10]
        }
    
    # Category analysis
    report['category_analysis'] = {
        'distribution': dict(category_counts),
        'patterns_per_category': {
            category: count for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        }
    }
    
    # Vendor analysis
    report['vendor_analysis'] = {
        'total_vendors': len(vendor_counts),
        'top_vendors': dict(sorted(vendor_counts.items(), key=lambda x: x[1], reverse=True)[:20]),
        'single_pattern_vendors': len([v for v, c in vendor_counts.items() if c == 1])
    }
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Advanced analytics report saved to: {output_file}")
    return report


def generate_visualizations(report_data, output_dir="analytics-visualizations"):
    """Generate visualizations from the analytics report."""
    print("Generating visualizations...")
    
    # Try to import matplotlib, but continue if not available
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping visualizations")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Category distribution pie chart
    categories = report_data['category_analysis']['distribution']
    plt.figure(figsize=(10, 8))
    plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
    plt.title('Pattern Distribution by Category')
    plt.savefig(os.path.join(output_dir, 'category_distribution.png'))
    plt.close()
    
    # Top vendors bar chart
    top_vendors = report_data['vendor_analysis']['top_vendors']
    vendors = list(top_vendors.keys())[:10]  # Top 10
    counts = list(top_vendors.values())[:10]
    
    plt.figure(figsize=(12, 6))
    plt.bar(vendors, counts)
    plt.title('Top 10 Vendors by Pattern Count')
    plt.xlabel('Vendor')
    plt.ylabel('Number of Patterns')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_vendors.png'))
    plt.close()
    
    # Complexity distribution
    complexity_dist = report_data['pattern_statistics']['complexity_distribution']
    plt.figure(figsize=(8, 6))
    plt.bar(complexity_dist.keys(), complexity_dist.values())
    plt.title('Pattern Complexity Distribution')
    plt.xlabel('Complexity Level')
    plt.ylabel('Number of Patterns')
    plt.savefig(os.path.join(output_dir, 'complexity_distribution.png'))
    plt.close()
    
    print(f"Visualizations saved to: {output_dir}")


def main():
    """Main function."""
    print("Advanced Analytics for Regex Intelligence Exchange")
    print("=" * 50)
    
    # Generate comprehensive report
    report = generate_comprehensive_report()
    
    # Generate visualizations
    generate_visualizations(report)
    
    # Print summary
    print(f"\nAnalytics Summary:")
    print(f"  Total Patterns: {report['summary']['total_patterns']}")
    print(f"  Total Regex Patterns: {report['summary']['total_regex_patterns']}")
    print(f"  Average Complexity Score: {report['summary']['avg_complexity_score']}")
    print(f"  Average Effectiveness Score: {report['summary']['avg_effectiveness_score']}")
    print(f"  Categories: {report['summary']['categories']}")
    print(f"  Vendors: {report['summary']['vendors']}")
    
    print(f"\nReport saved to: advanced-analytics-report.json")
    print(f"Visualizations saved to: analytics-visualizations/")


if __name__ == "__main__":
    main()