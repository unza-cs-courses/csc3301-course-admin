#!/usr/bin/env python3
"""
Prolog Test Runner for CSC3301
Runs SWI-Prolog tests for lab05 and proj04.

Usage:
    python3 run_prolog_tests.py <submission_path> <test_file>

Example:
    python3 run_prolog_tests.py ./csc3301-lab05-logic-programming ./hidden_tests/test_hidden.pl
"""

import os
import sys
import subprocess
import json
import shutil
import tempfile
from pathlib import Path


def check_prolog_installed():
    """Check if SWI-Prolog is installed."""
    prolog_path = shutil.which('swipl')
    if prolog_path:
        return prolog_path

    # Provide installation instructions
    print("=" * 60)
    print("ERROR: SWI-Prolog is not installed")
    print("=" * 60)
    print()
    print("To install SWI-Prolog:")
    print()
    print("  Ubuntu/Debian:")
    print("    sudo apt-get install swi-prolog")
    print()
    print("  macOS (Homebrew):")
    print("    brew install swi-prolog")
    print()
    print("  Windows:")
    print("    Download from https://www.swi-prolog.org/download/stable")
    print()
    print("After installation, re-run this script.")
    print("=" * 60)
    return None


def run_prolog_tests(submission_path: str, test_file: str, variant_config: dict = None):
    """
    Run Prolog tests on a student submission.

    Args:
        submission_path: Path to the student's submission directory
        test_file: Path to the test file (test_hidden.pl)
        variant_config: Optional variant configuration for the student

    Returns:
        dict with test results
    """
    prolog_path = check_prolog_installed()
    if not prolog_path:
        return {
            "error": "SWI-Prolog not installed",
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
            for pl_file in src_dir.glob("*.pl"):
                shutil.copy(pl_file, tmpdir / pl_file.name)

        # Copy test file
        test_copy = tmpdir / "test_hidden.pl"

        # Read and modify test file to use local paths
        with open(test_file, 'r') as f:
            test_content = f.read()

        # Update the load paths to be relative to tmpdir
        test_content = test_content.replace("['../../src/", "['")
        test_content = test_content.replace("['../../../", "['")

        # Apply variant configuration if provided
        if variant_config:
            for key, value in variant_config.items():
                if isinstance(value, str):
                    test_content = test_content.replace(f"${{{key}}}", value)
                else:
                    test_content = test_content.replace(f"${{{key}}}", str(value))

        with open(test_copy, 'w') as f:
            f.write(test_content)

        # Run Prolog tests
        try:
            result = subprocess.run(
                [
                    prolog_path,
                    "-s", str(test_copy),
                    "-g", "run_tests",
                    "-t", "halt"
                ],
                cwd=str(tmpdir),
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr

            # Parse test results from plunit output
            passed = 0
            failed = 0

            # Look for test result summary lines
            for line in output.split('\n'):
                if 'passed' in line.lower():
                    # Try to extract number
                    import re
                    match = re.search(r'(\d+)\s+passed', line.lower())
                    if match:
                        passed = int(match.group(1))
                if 'failed' in line.lower():
                    match = re.search(r'(\d+)\s+failed', line.lower())
                    if match:
                        failed = int(match.group(1))

            # Alternative: count test assertions
            if passed == 0 and failed == 0:
                passed = output.count('test passed')
                failed = output.count('test failed') + output.count('FAILED')

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

    results = run_prolog_tests(submission_path, test_file, variant_config)

    print(json.dumps(results, indent=2))

    if "error" in results:
        sys.exit(1)

    # Return non-zero if any tests failed
    if results.get("failed", 0) > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
