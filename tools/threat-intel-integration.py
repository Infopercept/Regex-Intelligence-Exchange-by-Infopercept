#!/usr/bin/env python3
"""
Threat Intelligence Integration for Regex Intelligence Exchange
"""

import json
import os
import sys
import requests
import re
from datetime import datetime
from pathlib import Path


def load_threat_intel_feeds():
    """Load threat intelligence feeds."""
    # This would typically connect to real threat intelligence APIs
    # For this example, we'll simulate with sample data
    
    sample_feeds = {
        "cve": [
            {
                "id": "CVE-2023-12345",
                "vendor": "Apache",
                "product": "HTTPD",
                "version_range": "2.4.0-2.4.52",
                "severity": "HIGH",
                "cvss_score": 8.1,
                "description": "Apache HTTP Server vulnerable to remote code execution",
                "references": [
                    "https://nvd.nist.gov/vuln/detail/CVE-2023-12345"
                ]
            },
            {
                "id": "CVE-2023-67890",
                "vendor": "Nginx",
                "product": "Nginx",
                "version_range": "1.20.0-1.22.1",
                "severity": "MEDIUM",
                "cvss_score": 6.5,
                "description": "Nginx HTTP request smuggling vulnerability",
                "references": [
                    "https://nvd.nist.gov/vuln/detail/CVE-2023-67890"
                ]
            }
        ],
        "exploits": [
            {
                "id": "EXP-2023-001",
                "vendor": "WordPress",
                "product": "WordPress",
                "version_range": "6.0.0-6.1.2",
                "exploit_type": "SQL Injection",
                "description": "SQL injection vulnerability in WordPress core",
                "references": [
                    "https://www.exploit-db.com/exploits/51234"
                ]
            }
        ]
    }
    
    return sample_feeds


def enrich_patterns_with_threat_intel(patterns_dir="patterns/by-vendor"):
    """Enrich existing patterns with threat intelligence data."""
    threat_intel = load_threat_intel_feeds()
    enriched_count = 0
    
    # Process each pattern file
    for root, dirs, files in os.walk(patterns_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                
                try:
                    # Load pattern
                    with open(file_path, 'r', encoding='utf-8') as f:
                        pattern_data = json.load(f)
                    
                    # Check if this pattern matches any threat intel
                    vendor = pattern_data.get('vendor', '')
                    product = pattern_data.get('product', '')
                    
                    # Look for matching CVEs
                    matching_cves = []
                    for cve in threat_intel.get('cve', []):
                        if (cve['vendor'].lower() == vendor.lower() and 
                            cve['product'].lower() == product.lower()):
                            matching_cves.append(cve)
                    
                    # Look for matching exploits
                    matching_exploits = []
                    for exploit in threat_intel.get('exploits', []):
                        if (exploit['vendor'].lower() == vendor.lower() and 
                            exploit['product'].lower() == product.lower()):
                            matching_exploits.append(exploit)
                    
                    # If we found matches, enrich the pattern
                    if matching_cves or matching_exploits:
                        # Add threat intel to metadata
                        if 'all_versions' in pattern_data:
                            for pattern in pattern_data['all_versions']:
                                if 'metadata' not in pattern:
                                    pattern['metadata'] = {}
                                
                                # Add CVE information
                                if matching_cves:
                                    if 'cwe_ids' not in pattern['metadata']:
                                        pattern['metadata']['cwe_ids'] = []
                                    
                                    for cve in matching_cves:
                                        if cve['id'] not in pattern['metadata']['cwe_ids']:
                                            pattern['metadata']['cwe_ids'].append(cve['id'])
                                
                                # Add exploit information
                                if matching_exploits:
                                    if 'references' not in pattern['metadata']:
                                        pattern['metadata']['references'] = []
                                    
                                    for exploit in matching_exploits:
                                        pattern['metadata']['references'].append({
                                            "title": f"Exploit: {exploit['description']}",
                                            "url": exploit['references'][0] if exploit['references'] else ""
                                        })
                        
                        # Add version-specific threat intel
                        if 'versions' in pattern_data:
                            for version_range, version_patterns in pattern_data['versions'].items():
                                for pattern in version_patterns:
                                    if 'metadata' not in pattern:
                                        pattern['metadata'] = {}
                                    
                                    # Add CVE information
                                    if matching_cves:
                                        if 'cwe_ids' not in pattern['metadata']:
                                            pattern['metadata']['cwe_ids'] = []
                                        
                                        for cve in matching_cves:
                                            # Check if version range matches
                                            if is_version_in_range(version_range, cve['version_range']):
                                                if cve['id'] not in pattern['metadata']['cwe_ids']:
                                                    pattern['metadata']['cwe_ids'].append(cve['id'])
                                    
                                    # Add exploit information
                                    if matching_exploits:
                                        if 'references' not in pattern['metadata']:
                                            pattern['metadata']['references'] = []
                                        
                                        for exploit in matching_exploits:
                                            # Check if version range matches
                                            if is_version_in_range(version_range, exploit['version_range']):
                                                pattern['metadata']['references'].append({
                                                    "title": f"Exploit: {exploit['description']}",
                                                    "url": exploit['references'][0] if exploit['references'] else ""
                                                })
                        
                        # Save enriched pattern
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(pattern_data, f, indent=2, ensure_ascii=False)
                        
                        enriched_count += 1
                        print(f"Enriched {vendor} {product} with threat intelligence")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    print(f"Enriched {enriched_count} patterns with threat intelligence")
    return enriched_count


def is_version_in_range(pattern_version, intel_version_range):
    """Check if a pattern version is in the threat intel version range."""
    # This is a simplified implementation
    # In a real system, this would need more sophisticated version comparison
    return True


def generate_threat_report(output_file="threat-intelligence-report.json"):
    """Generate a threat intelligence report."""
    threat_intel = load_threat_intel_feeds()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_cves": len(threat_intel.get('cve', [])),
            "total_exploits": len(threat_intel.get('exploits', [])),
            "high_severity_cves": len([c for c in threat_intel.get('cve', []) if c.get('severity') == 'HIGH']),
            "medium_severity_cves": len([c for c in threat_intel.get('cve', []) if c.get('severity') == 'MEDIUM'])
        },
        "cves": threat_intel.get('cve', []),
        "exploits": threat_intel.get('exploits', [])
    }
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Threat intelligence report saved to: {output_file}")
    return report


def main():
    """Main function."""
    print("Threat Intelligence Integration for Regex Intelligence Exchange")
    print("=" * 60)
    
    # Enrich patterns with threat intelligence
    print("\nEnriching patterns with threat intelligence...")
    enriched_count = enrich_patterns_with_threat_intel()
    
    # Generate threat report
    print("\nGenerating threat intelligence report...")
    report = generate_threat_report()
    
    print(f"\nThreat Intelligence Summary:")
    print(f"  Total CVEs: {report['summary']['total_cves']}")
    print(f"  High Severity CVEs: {report['summary']['high_severity_cves']}")
    print(f"  Medium Severity CVEs: {report['summary']['medium_severity_cves']}")
    print(f"  Total Exploits: {report['summary']['total_exploits']}")
    print(f"  Patterns Enriched: {enriched_count}")
    
    print(f"\nReport saved to: threat-intelligence-report.json")


if __name__ == "__main__":
    main()