"""Compatibility entry point for the current repository-local validator.

The archived implementation depended on a removed workspace layout. Its original
hash is retained in the portability change record; no historical run is repeated.
"""
from pathlib import Path
import subprocess
import sys

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    raise SystemExit(subprocess.call(
        [sys.executable, str(root / "tools/validate_research.py"), *sys.argv[1:]],
        cwd=root,
    ))
