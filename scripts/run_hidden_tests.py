#!/usr/bin/env python3
"""
Hidden Test Runner for CSC3301
Runs hidden tests on student submissions with variant awareness.

Usage:
    python run_hidden_tests.py --hidden-tests ~/csc3301-hidden-tests \
        --submissions ~/submissions/csc3301-lab01 \
        --assignment lab01-scope-binding \
        --output results.csv
"""
import json
import subprocess
import sys
import csv
import shutil
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import argparse


@dataclass
class TestResult:
    """Result of running hidden tests on a submission."""
    student_id: str
    repo_path: str
    tests_passed: int = 0
    tests_total: int = 0
    hidden_score: float = 0.0
    errors: List[str] = field(default_factory=list)
    test_details: Dict = field(default_factory=dict)


class HiddenTestRunner:
    """Runs hidden tests on cloned student repositories."""

    def __init__(
        self,
        hidden_tests_path: Path,
        submissions_path: Path,
        assignment_id: str,
        course_id: str = "csc3301"
    ):
        self.hidden_tests_path = hidden_tests_path / course_id / assignment_id
        self.submissions_path = submissions_path
        self.assignment_id = assignment_id
        self.course_id = course_id

        if not self.hidden_tests_path.exists():
            raise ValueError(f"Hidden tests not found: {self.hidden_tests_path}")

        # Detect language based on test files
        self.language = self._detect_language()

    def _detect_language(self) -> str:
        """Detect the programming language of the assignment."""
        if list(self.hidden_tests_path.glob("*.py")):
            return "python"
        elif list(self.hidden_tests_path.glob("*.rkt")):
            return "racket"
        elif list(self.hidden_tests_path.glob("*.pl")):
            return "prolog"
        return "python"  # Default

    def _load_variant_config(self, repo_path: Path) -> Optional[Dict]:
        """Load student's variant configuration."""
        for config_name in [".variant_config.json", "variant_config.json", "variant.json"]:
            config_file = repo_path / config_name
            if config_file.exists():
                with open(config_file) as f:
                    return json.load(f)
        return None

    def _extract_student_id(self, repo_path: Path) -> str:
        """Extract student ID from repository path."""
        # Repo name format: assignment-name-studentusername
        name = repo_path.name
        parts = name.split('-')
        if len(parts) >= 2:
            return parts[-1]
        return name

    def _run_python_tests(self, tmpdir: Path) -> Dict:
        """Run Python pytest tests."""
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/hidden/",
                "--json-report",
                "--json-report-file=hidden_results.json",
                "-v",
                "--tb=short"
            ],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=300
        )

        results_file = tmpdir / "hidden_results.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        return {"summary": {"passed": 0, "total": 0}, "error": result.stderr}

    def _check_interpreter(self, cmd: str, name: str, install_instructions: str) -> bool:
        """Check if an interpreter is installed and provide helpful message if not."""
        if shutil.which(cmd):
            return True

        print("=" * 60)
        print(f"ERROR: {name} is not installed")
        print("=" * 60)
        print()
        print(install_instructions)
        print()
        print("After installation, re-run this script.")
        print("=" * 60)
        return False

    def _run_racket_tests(self, tmpdir: Path) -> Dict:
        """Run Racket tests."""
        install_msg = """To install Racket:

  Ubuntu/Debian:
    sudo apt-get install racket

  macOS (Homebrew):
    brew install racket

  Windows:
    Download from https://racket-lang.org/download/"""

        if not self._check_interpreter("raco", "Racket", install_msg):
            return {
                "summary": {"passed": 0, "total": 0},
                "error": "Racket not installed - please install to run Scheme tests"
            }

        result = subprocess.run(
            ["raco", "test", "tests/hidden/"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse raco test output
        output = result.stdout + result.stderr
        passed = output.count("PASS") + output.count("passed")
        failed = output.count("FAIL") + output.count("failed")
        total = passed + failed

        return {
            "summary": {"passed": passed, "total": total},
            "output": output
        }

    def _run_prolog_tests(self, tmpdir: Path) -> Dict:
        """Run Prolog tests."""
        install_msg = """To install SWI-Prolog:

  Ubuntu/Debian:
    sudo apt-get install swi-prolog

  macOS (Homebrew):
    brew install swi-prolog

  Windows:
    Download from https://www.swi-prolog.org/download/stable"""

        if not self._check_interpreter("swipl", "SWI-Prolog", install_msg):
            return {
                "summary": {"passed": 0, "total": 0},
                "error": "SWI-Prolog not installed - please install to run Prolog tests"
            }

        test_files = list((tmpdir / "tests/hidden").glob("*.pl"))
        if not test_files:
            return {
                "summary": {"passed": 0, "total": 0},
                "error": "No Prolog test files found"
            }

        test_file = test_files[0]

        result = subprocess.run(
            ["swipl", "-s", str(test_file), "-g", "run_tests", "-t", "halt"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse plunit output
        output = result.stdout + result.stderr
        # Look for "X tests passed" pattern
        import re
        match = re.search(r"(\d+) tests passed", output)
        passed = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) tests failed", output)
        failed = int(match.group(1)) if match else 0

        total = passed + failed

        return {
            "summary": {"passed": passed, "total": total},
            "output": output
        }

    def run_on_submission(self, repo_path: Path) -> TestResult:
        """Run hidden tests on a single submission."""
        student_id = self._extract_student_id(repo_path)
        errors = []

        # Load variant config
        variant_config = self._load_variant_config(repo_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Copy student source code
            src_dir = repo_path / "src"
            if src_dir.exists():
                shutil.copytree(src_dir, tmpdir / "src")
            else:
                errors.append("No src/ directory found")
                return TestResult(
                    student_id=student_id,
                    repo_path=str(repo_path),
                    errors=errors
                )

            # Copy hidden tests
            shutil.copytree(self.hidden_tests_path, tmpdir / "tests/hidden")

            # Write variant config for tests to read
            if variant_config:
                with open(tmpdir / "variant_config.json", 'w') as f:
                    json.dump(variant_config, f)

            # Copy any additional requirements
            req_file = repo_path / "requirements.txt"
            if req_file.exists():
                shutil.copy(req_file, tmpdir / "requirements.txt")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
                    cwd=tmpdir,
                    capture_output=True
                )

            # Run tests based on language
            try:
                if self.language == "python":
                    results = self._run_python_tests(tmpdir)
                elif self.language == "racket":
                    results = self._run_racket_tests(tmpdir)
                elif self.language == "prolog":
                    results = self._run_prolog_tests(tmpdir)
                else:
                    results = self._run_python_tests(tmpdir)

                passed = results.get("summary", {}).get("passed", 0)
                total = results.get("summary", {}).get("total", 0)
                score = (passed / total * 100) if total > 0 else 0

                if "error" in results:
                    errors.append(results["error"][:500])

            except subprocess.TimeoutExpired:
                errors.append("Test execution timed out")
                passed, total, score = 0, 0, 0
            except Exception as e:
                errors.append(f"Test execution failed: {str(e)[:200]}")
                passed, total, score = 0, 0, 0

        return TestResult(
            student_id=student_id,
            repo_path=str(repo_path),
            tests_passed=passed,
            tests_total=total,
            hidden_score=score,
            errors=errors,
            test_details=results if 'results' in dir() else {}
        )

    def run_all(self, verbose: bool = True) -> List[TestResult]:
        """Run hidden tests on all submissions."""
        results = []

        submissions = [
            p for p in self.submissions_path.iterdir()
            if p.is_dir() and not p.name.startswith('.')
        ]

        if verbose:
            print(f"Found {len(submissions)} submissions to test")
            print(f"Hidden tests: {self.hidden_tests_path}")
            print(f"Language: {self.language}")
            print()

        for i, repo_path in enumerate(sorted(submissions)):
            if verbose:
                print(f"[{i+1}/{len(submissions)}] Testing: {repo_path.name}")

            try:
                result = self.run_on_submission(repo_path)
                results.append(result)

                if verbose:
                    status = "✓" if result.hidden_score >= 70 else "✗"
                    print(f"  {status} Score: {result.hidden_score:.1f}% "
                          f"({result.tests_passed}/{result.tests_total})")
                    if result.errors:
                        print(f"  Errors: {result.errors[0][:80]}...")

            except Exception as e:
                if verbose:
                    print(f"  ERROR: {e}")
                results.append(TestResult(
                    student_id=self._extract_student_id(repo_path),
                    repo_path=str(repo_path),
                    errors=[str(e)]
                ))

        return results

    def export_results(self, results: List[TestResult], output_file: Path):
        """Export results to CSV."""
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Student ID', 'Repository', 'Tests Passed', 'Tests Total',
                'Hidden Score', 'Errors'
            ])
            for r in sorted(results, key=lambda x: x.student_id):
                writer.writerow([
                    r.student_id,
                    r.repo_path,
                    r.tests_passed,
                    r.tests_total,
                    f"{r.hidden_score:.1f}",
                    "; ".join(r.errors)
                ])

        print(f"\nResults exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run hidden tests on student submissions"
    )
    parser.add_argument(
        "--hidden-tests", "-t",
        type=Path,
        required=True,
        help="Path to hidden tests repository"
    )
    parser.add_argument(
        "--submissions", "-s",
        type=Path,
        required=True,
        help="Path to cloned student submissions"
    )
    parser.add_argument(
        "--assignment", "-a",
        required=True,
        help="Assignment ID (e.g., lab01-scope-binding)"
    )
    parser.add_argument(
        "--course", "-c",
        default="csc3301",
        help="Course ID (default: csc3301)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("hidden_results.csv"),
        help="Output CSV file"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )

    args = parser.parse_args()

    runner = HiddenTestRunner(
        hidden_tests_path=args.hidden_tests,
        submissions_path=args.submissions,
        assignment_id=args.assignment,
        course_id=args.course
    )

    results = runner.run_all(verbose=not args.quiet)
    runner.export_results(results, args.output)

    # Print summary
    if not args.quiet:
        scores = [r.hidden_score for r in results]
        print(f"\n=== Summary ===")
        print(f"Total submissions: {len(results)}")
        print(f"Average score: {sum(scores)/len(scores):.1f}%")
        print(f"Passing (>=70%): {sum(1 for s in scores if s >= 70)}")
        print(f"Failing (<70%): {sum(1 for s in scores if s < 70)}")


if __name__ == "__main__":
    main()
