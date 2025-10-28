#!/usr/bin/env python3
"""
Quality monitoring script for pattern files
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def find_pattern_files(root_dir):
    """Find all pattern files in the repository."""
    pattern_files = []
    patterns_dir = os.path.join(root_dir, 'patterns')
    
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                pattern_files.append(os.path.join(root, file))
    
    return pattern_files


def check_pattern_quality(file_path):
    """
    Check the quality of a pattern file.
    
    Args:
        file_path (str): Path to the pattern file
        
    Returns:
        dict: Quality report
    """
    report = {
        'file': file_path,
        'total_patterns': 0,
        'patterns_with_test_cases': 0,
        'patterns_with_references': 0,
        'patterns_with_severity': 0,
        'patterns_with_cvss': 0,
        'patterns_with_cwe': 0,
        'patterns_with_affected_versions': 0,
        'patterns_with_remediation': 0,
        'patterns_with_source': 0,
        'patterns_with_license': 0,
        'issues': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check top-level fields
        if 'vendor' not in data:
            report['issues'].append("Missing vendor field")
        if 'product' not in data:
            report['issues'].append("Missing product field")
        if 'category' not in data:
            report['issues'].append("Missing category field")
        if 'subcategory' not in data:
            report['issues'].append("Missing subcategory field")
        
        # Check all_versions patterns
        all_versions = data.get('all_versions', [])
        for i, pattern in enumerate(all_versions):
            report['total_patterns'] += 1
            pattern_id = f"all_versions[{i}]"
            check_pattern_fields(pattern, pattern_id, report)
        
        # Check version-specific patterns
        versions = data.get('versions', {})
        for version_range, version_patterns in versions.items():
            for i, pattern in enumerate(version_patterns):
                report['total_patterns'] += 1
                pattern_id = f"versions.{version_range}[{i}]"
                check_pattern_fields(pattern, pattern_id, report)
        
        return report
    except Exception as e:
        report['issues'].append(f"Error processing file: {e}")
        return report


def check_pattern_fields(pattern, pattern_id, report):
    """
    Check individual pattern fields for quality.
    
    Args:
        pattern (dict): Pattern data
        pattern_id (str): Pattern identifier for reporting
        report (dict): Quality report to update
    """
    # Check required fields
    if 'name' not in pattern:
        report['issues'].append(f"{pattern_id}: Missing name field")
    if 'pattern' not in pattern:
        report['issues'].append(f"{pattern_id}: Missing pattern field")
    if 'version_group' not in pattern:
        report['issues'].append(f"{pattern_id}: Missing version_group field")
    if 'priority' not in pattern:
        report['issues'].append(f"{pattern_id}: Missing priority field")
    if 'confidence' not in pattern:
        report['issues'].append(f"{pattern_id}: Missing confidence field")
    
    # Check metadata
    if 'metadata' in pattern:
        metadata = pattern['metadata']
        
        # Check for test cases
        if 'test_cases' in metadata and metadata['test_cases']:
            report['patterns_with_test_cases'] += 1
        else:
            report['issues'].append(f"{pattern_id}: No test cases provided")
        
        # Check for references
        if 'references' in metadata and metadata['references']:
            report['patterns_with_references'] += 1
        
        # Check for severity
        if 'severity' in metadata:
            report['patterns_with_severity'] += 1
        
        # Check for CVSS score
        if 'cvss_score' in metadata:
            report['patterns_with_cvss'] += 1
        
        # Check for CWE IDs
        if 'cwe_ids' in metadata and metadata['cwe_ids']:
            report['patterns_with_cwe'] += 1
        
        # Check for affected versions
        if 'affected_versions' in metadata and metadata['affected_versions']:
            report['patterns_with_affected_versions'] += 1
        
        # Check for remediation
        if 'remediation' in metadata:
            report['patterns_with_remediation'] += 1
        
        # Check for source
        if 'source' in metadata:
            report['patterns_with_source'] += 1
        
        # Check for license
        if 'license' in metadata:
            report['patterns_with_license'] += 1
        
        # Check date formats
        date_fields = ['created_at', 'updated_at']
        for field in date_fields:
            if field in metadata:
                try:
                    datetime.strptime(metadata[field], '%Y-%m-%d')
                except ValueError:
                    try:
                        datetime.strptime(metadata[field], '%Y-%m-%dT%H:%M:%S')
                    except ValueError:
                        report['issues'].append(f"{pattern_id}: {field} has invalid date format")
    else:
        report['issues'].append(f"{pattern_id}: Missing metadata")


def generate_quality_report(reports):
    """
    Generate a summary quality report.
    
    Args:
        reports (list): List of individual file reports
        
    Returns:
        dict: Summary report
    """
    summary = {
        'total_files': len(reports),
        'total_patterns': sum(r['total_patterns'] for r in reports),
        'patterns_with_test_cases': sum(r['patterns_with_test_cases'] for r in reports),
        'patterns_with_references': sum(r['patterns_with_references'] for r in reports),
        'patterns_with_severity': sum(r['patterns_with_severity'] for r in reports),
        'patterns_with_cvss': sum(r['patterns_with_cvss'] for r in reports),
        'patterns_with_cwe': sum(r['patterns_with_cwe'] for r in reports),
        'patterns_with_affected_versions': sum(r['patterns_with_affected_versions'] for r in reports),
        'patterns_with_remediation': sum(r['patterns_with_remediation'] for r in reports),
        'patterns_with_source': sum(r['patterns_with_source'] for r in reports),
        'patterns_with_license': sum(r['patterns_with_license'] for r in reports),
        'files_with_issues': sum(1 for r in reports if r['issues']),
        'total_issues': sum(len(r['issues']) for r in reports),
        'test_case_coverage': 0.0,
        'reference_coverage': 0.0,
        'severity_coverage': 0.0,
        'cvss_coverage': 0.0,
        'cwe_coverage': 0.0,
        'affected_versions_coverage': 0.0,
        'remediation_coverage': 0.0,
        'source_coverage': 0.0,
        'license_coverage': 0.0
    }
    
    # Calculate percentages
    if summary['total_patterns'] > 0:
        summary['test_case_coverage'] = float((summary['patterns_with_test_cases'] / summary['total_patterns']) * 100)
        summary['reference_coverage'] = float((summary['patterns_with_references'] / summary['total_patterns']) * 100)
        summary['severity_coverage'] = float((summary['patterns_with_severity'] / summary['total_patterns']) * 100)
        summary['cvss_coverage'] = float((summary['patterns_with_cvss'] / summary['total_patterns']) * 100)
        summary['cwe_coverage'] = float((summary['patterns_with_cwe'] / summary['total_patterns']) * 100)
        summary['affected_versions_coverage'] = float((summary['patterns_with_affected_versions'] / summary['total_patterns']) * 100)
        summary['remediation_coverage'] = float((summary['patterns_with_remediation'] / summary['total_patterns']) * 100)
        summary['source_coverage'] = float((summary['patterns_with_source'] / summary['total_patterns']) * 100)
        summary['license_coverage'] = float((summary['patterns_with_license'] / summary['total_patterns']) * 100)
    
    return summary


def print_quality_report(summary, reports, show_details=False):
    """
    Print the quality report.
    
    Args:
        summary (dict): Summary report
        reports (list): Individual file reports
        show_details (bool): Whether to show detailed reports
    """
    print("=" * 60)
    print("PATTERN QUALITY REPORT")
    print("=" * 60)
    
    print(f"Total Files: {summary['total_files']}")
    print(f"Total Patterns: {summary['total_patterns']}")
    print(f"Files with Issues: {summary['files_with_issues']}")
    print(f"Total Issues: {summary['total_issues']}")
    print()
    
    if summary['total_patterns'] > 0:
        print("METADATA COVERAGE:")
        print(f"  Test Cases: {summary['test_case_coverage']:.1f}% ({summary['patterns_with_test_cases']}/{summary['total_patterns']})")
        print(f"  References: {summary['reference_coverage']:.1f}% ({summary['patterns_with_references']}/{summary['total_patterns']})")
        print(f"  Severity: {summary['severity_coverage']:.1f}% ({summary['patterns_with_severity']}/{summary['total_patterns']})")
        print(f"  CVSS Score: {summary['cvss_coverage']:.1f}% ({summary['patterns_with_cvss']}/{summary['total_patterns']})")
        print(f"  CWE IDs: {summary['cwe_coverage']:.1f}% ({summary['patterns_with_cwe']}/{summary['total_patterns']})")
        print(f"  Affected Versions: {summary['affected_versions_coverage']:.1f}% ({summary['patterns_with_affected_versions']}/{summary['total_patterns']})")
        print(f"  Remediation: {summary['remediation_coverage']:.1f}% ({summary['patterns_with_remediation']}/{summary['total_patterns']})")
        print(f"  Source: {summary['source_coverage']:.1f}% ({summary['patterns_with_source']}/{summary['total_patterns']})")
        print(f"  License: {summary['license_coverage']:.1f}% ({summary['patterns_with_license']}/{summary['total_patterns']})")
    
    if show_details:
        print("\nDETAILED ISSUES:")
        for report in reports:
            if report['issues']:
                print(f"\n{report['file']}:")
                for issue in report['issues']:
                    print(f"  - {issue}")


def main():
    """Main function."""
    # Get the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    
    # Parse command line arguments
    show_details = '--details' in sys.argv
    target_file = None
    for arg in sys.argv[1:]:
        if arg != '--details':
            target_file = arg
            break
    
    # Check if a specific file was provided
    if target_file:
        if not os.path.exists(target_file):
            print(f"Error: File not found: {target_file}")
            return 1
        
        report = check_pattern_quality(target_file)
        summary = generate_quality_report([report])
        print_quality_report(summary, [report], show_details)
        
        if report['issues']:
            return 1
        else:
            return 0
    else:
        print("Analyzing pattern quality across repository...")
        
        # Find all pattern files
        pattern_files = find_pattern_files(repo_root)
        
        if not pattern_files:
            print("No pattern files found!")
            return 1
        
        print(f"Found {len(pattern_files)} pattern files to analyze")
        
        # Check quality of each pattern file
        reports = []
        for pattern_file in pattern_files:
            try:
                report = check_pattern_quality(pattern_file)
                reports.append(report)
            except Exception as e:
                print(f"Error analyzing {pattern_file}: {e}")
        
        # Generate and print summary report
        summary = generate_quality_report(reports)
        print_quality_report(summary, reports, show_details)
        
        # Return exit code based on issues found
        if summary['total_issues'] > 0:
            return 1
        else:
            return 0


if __name__ == "__main__":
    sys.exit(main())