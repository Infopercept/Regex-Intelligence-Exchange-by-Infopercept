#!/usr/bin/env python3
"""
Compatibility wrapper for legacy script name used by tests/docs.
Delegates to `check-duplicates.py` which implements the actual logic.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure tools package path is usable when executed from repo root
TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))

try:
    # Import the real implementation
    from check_duplicates import main as _main_fn  # type: ignore
except Exception:
    try:
        # fallback to module name with dash if present
        from check_duplicates import main as _main_fn  # type: ignore
    except Exception:
        # Try importing by filename module
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("check_duplicates", str(TOOLS_DIR / "check-duplicates.py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            _main_fn = getattr(module, 'main', None)
        except Exception:
            _main_fn = None


def main(argv=None):
    """Run the duplicate checker implementation."""
    if _main_fn is None:
        print("Error: underlying duplicate checker implementation not found (expected tools/check-duplicates.py)")
        return 1

    # If the underlying main expects no args and reads files itself, just call it
    try:
        if argv is None:
            return _main_fn()
        else:
            return _main_fn()
    except TypeError:
        # If implementation doesn't accept args
        _main_fn()
        return 0


if __name__ == '__main__':
    sys.exit(main())


# Additional helpers expected by tests
def calculate_similarity(pat_a, pat_b):
    """Calculate a similarity score between two pattern dicts.

    This is a lightweight similarity function used by the test-suite.
    It returns 1.0 for identical inputs, and a value in [0,1].
    """
    try:
        from difflib import SequenceMatcher
    except Exception:
        # fallback: identical check
        if pat_a == pat_b:
            return 1.0
        return 0.0

    def normalize(d):
        if not isinstance(d, dict):
            return ''
        parts = []
        for key in ('name', 'pattern', 'vendor', 'product'):
            v = d.get(key, '')
            if v is None:
                v = ''
            parts.append(str(v).lower())
        s = '||'.join(parts)
        return s

    s1 = normalize(pat_a)
    s2 = normalize(pat_b)

    # Both empty => identical
    if s1 == '' and s2 == '':
        return 1.0

    ratio = SequenceMatcher(None, s1, s2).ratio()
    return float(ratio)

