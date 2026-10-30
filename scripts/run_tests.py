"""
PhishGuard Unified Test Runner
Runs all machine learning, feature extraction, leakage prevention, and backend API tests.
"""

from __future__ import annotations
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_all_tests():
    print("=" * 65)
    print("Executing PhishGuard Complete Automated Test Suite")
    print("=" * 65)

    cmd = [sys.executable, "-m", "pytest", "ml/tests", "backend/tests", "-v"]
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    
    if result.returncode == 0:
        print("\n" + "=" * 65)
        print("ALL PHISHGUARD AUTOMATED TESTS PASSED SUCCESSFULLY! (Code 0)")
        print("=" * 65)
    else:
        print("\n" + "=" * 65)
        print(f"SOME TESTS FAILED! (Exit code: {result.returncode})")
        print("=" * 65)

    sys.exit(result.returncode)


if __name__ == "__main__":
    run_all_tests()
