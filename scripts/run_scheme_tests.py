#!/usr/bin/env python3
"""
Scheme/Racket Test Runner for CSC3301
Runs Racket tests for proj02-symbolic-differentiator.

Usage:
    python3 run_scheme_tests.py <submission_path> <test_file>

Example:
    python3 run_scheme_tests.py ./csc3301-proj02-symbolic-differentiator ./hidden_tests/test_hidden.rkt
"""

import os
import sys
import subprocess
import json
import shutil
import tempfile
from pathlib import Path


def check_racket_installed():
    """Check if Racket is installed."""
    racket_path = shutil.which('racket')
    if racket_path:
        return racket_path

    # Also check for raco (Racket's package manager/test runner)
    raco_path = shutil.which('raco')

    # Provide installation instructions
    print("=" * 60)
    print("ERROR: Racket is not installed")
    print("=" * 60)
    print()
    print("To install Racket:")
    print()
    print("  Ubuntu/Debian:")
    print("    sudo apt-get install racket")
    print()
    print("  macOS (Homebrew):")
    print("    brew install racket")
    print()
    print("  Windows:")
    print("    Download from https://racket-lang.org/download/")
    print()
    print("After installation, re-run this script.")
    print("=" * 60)
    return None


def run_scheme_tests(submission_path: str, test_file: str, variant_config: dict = None):
    """
    Run Scheme/Racket tests on a student submission.

    Args:
        submission_path: Path to the student's submission directory
        test_file: Path to the test file (test_hidden.rkt)
        variant_config: Optional variant configuration for the student

    Returns:
        dict with test results
    """
    racket_path = check_racket_installed()
    if not racket_path:
        return {
            "error": "Racket not installed",
            "passed": 0,
            "failed": 0,
            "total": 0
        }

    submission_path = Path(submission_path).resolve()
    test_file = Path(test_file).resolve()

    if not submission_path.exists():
        return {"error": f"Submission path not found: {submission_path}"}

    if not test_file.exists():
        return {"error": f"Test file not found: {test_file}"}

    # Create a temporary directory to run tests
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Copy student source files
        src_dir = submission_path / "src"
        if src_dir.exists():
            for rkt_file in src_dir.glob("*.rkt"):
                shutil.copy(rkt_file, tmpdir / rkt_file.name)
            for scm_file in src_dir.glob("*.scm"):
                shutil.copy(scm_file, tmpdir / scm_file.name)

        # Copy test file
        test_copy = tmpdir / "test_hidden.rkt"

        # Read and modify test file to use local paths
        with open(test_file, 'r') as f:
            test_content = f.read()

        # Update the require paths to be relative to tmpdir
        test_content = test_content.replace('(require "../../src/', '(require "./')
        test_content = test_content.replace('(require "../../../', '(require "./')

        # Apply variant configuration if provided
        if variant_config:
            for key, value in variant_config.items():
                if isinstance(value, str):
                    test_content = test_content.replace(f"${{{key}}}", value)
                else:
                    test_content = test_content.replace(f"${{{key}}}", str(value))

        with open(test_copy, 'w') as f:
            f.write(test_content)

        # Try running with raco test first
        raco_path = shutil.which('raco')

        try:
            if raco_path:
                result = subprocess.run(
                    [raco_path, "test", str(test_copy)],
                    cwd=str(tmpdir),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                # Fall back to running racket directly
                result = subprocess.run(
                    [racket_path, str(test_copy)],
                    cwd=str(tmpdir),
                    capture_output=True,
                    text=True,
                    timeout=60
                )

            output = result.stdout + result.stderr

            # Parse test results from rackunit output
            passed = 0
            failed = 0

            # Look for rackunit test result summary
            import re

            # Pattern: "X tests passed"
            match = re.search(r'(\d+)\s+tests?\s+passed', output, re.IGNORECASE)
            if match:
                passed = int(match.group(1))

            # Pattern: "X tests failed"
            match = re.search(r'(\d+)\s+tests?\s+failed', output, re.IGNORECASE)
            if match:
                failed = int(match.group(1))

            # Alternative patterns
            if passed == 0 and failed == 0:
                # Count check-equal? success/failure
                passed = output.lower().count('ok')
                failed = output.lower().count('failure') + output.lower().count('error')

            return {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "output": output,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "error": "Test execution timed out (60s limit)",
                "passed": 0,
                "failed": 0,
                "total": 0
            }
        except Exception as e:
            return {
                "error": str(e),
                "passed": 0,
                "failed": 0,
                "total": 0
            }


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    submission_path = sys.argv[1]
    test_file = sys.argv[2]

    # Load variant config if available
    variant_config = None
    variant_file = Path(submission_path) / ".variant_config.json"
    if variant_file.exists():
        with open(variant_file) as f:
            variant_config = json.load(f)

    results = run_scheme_tests(submission_path, test_file, variant_config)

    print(json.dumps(results, indent=2))

    if "error" in results:
        sys.exit(1)

    # Return non-zero if any tests failed
    if results.get("failed", 0) > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
