#!/usr/bin/env python3
"""
Compatibility wrapper for legacy `test-patterns.py` name used by tests/docs.
Delegates to `pattern-matcher.py` implementation which provides matching/test functionality.
"""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

try:
    # import pattern-matcher module
    from pattern_matcher import main as _pm_main  # type: ignore
except Exception:
    try:
        # try loading by filename
        import importlib.util
        spec = importlib.util.spec_from_file_location("pattern_matcher", str(TOOLS_DIR / "pattern-matcher.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        _pm_main = getattr(module, 'main', None)
    except Exception:
        _pm_main = None


def main(argv=None):
    if _pm_main is None:
        print("Error: underlying pattern tester implementation not found (expected tools/pattern-matcher.py)")
        return 1

    # Delegate to the underlying main function. pattern-matcher's main reads sys.argv, so simulate that.
    if argv is not None:
        # Provide argv as arguments to the underlying main via sys.argv
        old_argv = sys.argv
        try:
            sys.argv = [old_argv[0]] + list(argv)
            return _pm_main()
        finally:
            sys.argv = old_argv
    else:
        return _pm_main()


if __name__ == '__main__':
    sys.exit(main())


# Functions expected by the test-suite -------------------------------------
import re
import json
from typing import Tuple, Any, Optional


def validate_json_structure(file_path: str) -> Tuple[bool, Optional[Any], Optional[str]]:
    """Validate that a file contains valid JSON. Returns (ok, data, message)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON: {e}"
    except Exception as e:
        return False, None, f"Error reading file: {e}"


def validate_pattern_structure(pattern: dict, file_name: str, pattern_name: str) -> Tuple[bool, str]:
    """Lightweight pattern structure validation used by tests."""
    required = ['name', 'pattern']
    for r in required:
        if r not in pattern:
            return False, f"Missing required field '{r}' in {pattern_name} ({file_name})"
    # Basic pattern compilation check
    try:
        re.compile(pattern['pattern'])
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"
    return True, "Structure validation passed"


def validate_metadata(metadata: dict, context: str) -> Tuple[bool, str]:
    """Basic metadata validation."""
    if not isinstance(metadata, dict):
        return False, "Metadata must be an object"
    # Minimal checks
    if 'author' not in metadata or 'created_at' not in metadata:
        return False, "Missing required metadata fields"
    return True, "Metadata validation passed"


def run_test_cases(pattern: dict, file_name: str) -> Tuple[bool, str]:
    """Execute test cases embedded in a pattern's metadata.

    Returns (success, message).
    """
    tests = pattern.get('metadata', {}).get('test_cases')
    if not tests:
        return True, "No test cases to run"

    regex = pattern.get('pattern')
    if not regex:
        return False, "No regex pattern provided"

    try:
        compiled = re.compile(regex)
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"

    failed = 0
    for tc in tests:
        input_text = tc.get('input', '')
        expected_version = tc.get('expected_version')
        m = compiled.search(input_text)
        if not m:
            failed += 1
            continue
        # Get first group if present
        version = m.group(1) if m.groups() else None
        if expected_version is not None:
            if str(version) != str(expected_version):
                failed += 1

    if failed > 0:
        return False, f"{failed} test(s) failed"
    return True, f"{len(tests)} test cases passed"

