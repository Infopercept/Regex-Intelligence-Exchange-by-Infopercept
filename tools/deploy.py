#!/usr/bin/env python3
"""
Deployment script for Regex Intelligence Exchange
"""

import json
import os
import sys
import subprocess
import argparse
from datetime import datetime


def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return True, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def validate_environment():
    """Validate that the deployment environment is ready."""
    print("Validating deployment environment...")
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        return False
    
    # Check required tools
    required_tools = ['git', 'python']
    for tool in required_tools:
        success, _, _ = run_command(f"which {tool}")
        if not success:
            success, _, _ = run_command(f"where {tool}")
            if not success:
                print(f"Error: Required tool '{tool}' not found")
                return False
    
    print("Environment validation passed")
    return True


def run_tests():
    """Run all test suites."""
    print("Running test suites...")
    
    # Run unit tests
    success, stdout, stderr = run_command("python tests/run_tests.py")
    if not success:
        print(f"Unit tests failed: {stderr}")
        return False
    
    print("Unit tests passed")
    
    # Run performance tests
    success, stdout, stderr = run_command("python tests/test_performance.py")
    if not success:
        print(f"Performance tests failed: {stderr}")
        return False
    
    print("Performance tests passed")
    return True


def validate_patterns():
    """Validate all pattern files."""
    print("Validating pattern files...")
    
    success, stdout, stderr = run_command("python tools/validate-all-patterns.py")
    if not success:
        print(f"Pattern validation failed: {stderr}")
        return False
    
    print("Pattern validation passed")
    return True


def optimize_patterns():
    """Optimize pattern files for performance."""
    print("Optimizing pattern files...")
    
    success, stdout, stderr = run_command("python tools/optimize-patterns.py")
    if not success:
        print(f"Pattern optimization failed: {stderr}")
        return False
    
    print("Pattern optimization completed")
    return True


def check_duplicates():
    """Check for duplicate patterns."""
    print("Checking for duplicate patterns...")
    
    success, stdout, stderr = run_command("python tools/enhanced-duplicate-checker.py")
    if not success:
        print(f"Duplicate check failed: {stderr}")
        return False
    
    print("Duplicate check completed")
    return True


def update_documentation():
    """Update documentation files."""
    print("Updating documentation...")
    
    # Update pattern summary
    success, stdout, stderr = run_command("python tools/generate-pattern-summary.py")
    if not success:
        print(f"Pattern summary generation failed: {stderr}")
        return False
    
    # Update patterns report
    success, stdout, stderr = run_command("python tools/generate-patterns-report.py")
    if not success:
        print(f"Patterns report generation failed: {stderr}")
        return False
    
    print("Documentation updated")
    return True


def create_release_tag(version):
    """Create a Git tag for the release."""
    print(f"Creating release tag v{version}...")
    
    # Check if tag already exists
    success, stdout, stderr = run_command(f"git tag -l v{version}")
    if stdout.strip():
        print(f"Warning: Tag v{version} already exists")
        return True
    
    # Create and push tag
    commands = [
        f"git tag -a v{version} -m 'Release version {version}'",
        f"git push origin v{version}"
    ]
    
    for command in commands:
        success, stdout, stderr = run_command(command)
        if not success:
            print(f"Failed to execute '{command}': {stderr}")
            return False
    
    print(f"Release tag v{version} created and pushed")
    return True


def generate_release_notes(version):
    """Generate release notes."""
    print(f"Generating release notes for v{version}...")
    
    release_notes = f"""# Regex Intelligence Exchange v{version}

## Release Date
{datetime.now().strftime('%Y-%m-%d')}

## Overview
This release includes performance improvements, bug fixes, and new pattern additions.

## Changelog

### Features
- Enhanced pattern categorization with subcategories
- Improved version extraction algorithms
- Additional metadata fields for better documentation
- Integration with Wappalyzer and WebTech databases
- Enhanced validation and testing framework

### Performance Improvements
- Optimized pattern matching performance
- Precompiled regex patterns for faster execution
- Performance cache for faster pattern loading

### Bug Fixes
- Fixed pattern structure inconsistencies
- Improved duplicate detection and management
- Enhanced metadata completeness

### Documentation
- Updated all documentation files
- Added comprehensive test suite
- Created detailed release procedure

## Upgrade Instructions
To upgrade to this version:

```bash
git pull origin main
python tools/update-patterns.py
python tools/optimize-patterns.py
```

## Support
For issues or questions, please open a GitHub issue or contact the maintainers.
"""
    
    # Write release notes to file
    release_notes_file = f"RELEASE_NOTES_v{version}.md"
    try:
        with open(release_notes_file, 'w', encoding='utf-8') as f:
            f.write(release_notes)
        print(f"Release notes written to {release_notes_file}")
        return True
    except Exception as e:
        print(f"Failed to write release notes: {e}")
        return False


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy Regex Intelligence Exchange')
    parser.add_argument('--version', required=True, help='Version number for release')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--skip-validation', action='store_true', help='Skip pattern validation')
    parser.add_argument('--skip-optimization', action='store_true', help='Skip pattern optimization')
    parser.add_argument('--skip-duplicates', action='store_true', help='Skip duplicate checking')
    parser.add_argument('--skip-documentation', action='store_true', help='Skip documentation updates')
    
    args = parser.parse_args()
    
    print(f"Starting deployment for version {args.version}")
    
    # Validate environment
    if not validate_environment():
        print("Environment validation failed")
        return 1
    
    # Run tests (unless skipped)
    if not args.skip_tests:
        if not run_tests():
            print("Tests failed")
            return 1
    
    # Validate patterns (unless skipped)
    if not args.skip_validation:
        if not validate_patterns():
            print("Pattern validation failed")
            return 1
    
    # Optimize patterns (unless skipped)
    if not args.skip_optimization:
        if not optimize_patterns():
            print("Pattern optimization failed")
            return 1
    
    # Check duplicates (unless skipped)
    if not args.skip_duplicates:
        if not check_duplicates():
            print("Duplicate check failed")
            return 1
    
    # Update documentation (unless skipped)
    if not args.skip_documentation:
        if not update_documentation():
            print("Documentation update failed")
            return 1
    
    # Generate release notes
    if not generate_release_notes(args.version):
        print("Failed to generate release notes")
        return 1
    
    # Create release tag
    if not create_release_tag(args.version):
        print("Failed to create release tag")
        return 1
    
    print(f"\nDeployment completed successfully for version {args.version}!")
    print(f"Release notes: RELEASE_NOTES_v{args.version}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())