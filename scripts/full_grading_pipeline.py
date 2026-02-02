#!/usr/bin/env python3
"""
Full Grading Pipeline for CSC3301
Orchestrates the complete grading workflow from cloning to grade export.

Usage:
    python full_grading_pipeline.py --course csc3301 --assignment lab01-scope-binding

Steps:
1. Clone all student submissions
2. Run visible tests (extract from GitHub Actions or run locally)
3. Run hidden tests (variant-aware)
4. Run plagiarism detection (JPlag)
5. Calculate final grades with weights
6. Export to LMS-compatible CSV
"""
import subprocess
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import argparse


@dataclass
class PipelineConfig:
    """Configuration for the grading pipeline."""
    course_id: str
    assignment_id: str
    grading_home: Path
    organization: str = "unza-cs-courses"
    hidden_tests_repo: Optional[Path] = None
    weights: dict = None

    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "visible_tests": 0.40,
                "hidden_tests": 0.30,
                "code_quality": 0.20,
                "plagiarism_penalty_max": 0.10
            }

        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        self.submissions_dir = self.grading_home / "submissions" / f"{self.course_id}-{self.assignment_id}"
        self.grades_dir = self.grading_home / "grades" / self.course_id
        self.reports_dir = self.grading_home / "plagiarism-reports" / f"{self.course_id}-{self.assignment_id}-{self.timestamp}"

        if self.hidden_tests_repo is None:
            self.hidden_tests_repo = self.grading_home / "hidden-tests"


class GradingPipeline:
    """Complete grading pipeline orchestrator."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.scripts_dir = Path(__file__).parent

        # Ensure directories exist
        self.config.submissions_dir.mkdir(parents=True, exist_ok=True)
        self.config.grades_dir.mkdir(parents=True, exist_ok=True)
        self.config.reports_dir.mkdir(parents=True, exist_ok=True)

    def step1_clone_submissions(self) -> bool:
        """Clone all student submissions from GitHub Classroom."""
        print("\n" + "=" * 60)
        print("STEP 1: Cloning Student Submissions")
        print("=" * 60)

        clone_script = self.scripts_dir / "clone_submissions.sh"

        if clone_script.exists():
            result = subprocess.run(
                ["bash", str(clone_script), f"{self.config.course_id}-{self.config.assignment_id}"],
                cwd=self.config.grading_home,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode != 0:
                print(f"Warning: {result.stderr}")
        else:
            # Fallback: use gh CLI directly
            print("Using gh CLI to clone repositories...")
            result = subprocess.run(
                [
                    "gh", "repo", "list", self.config.organization,
                    "--json", "name", "--jq", ".[].name"
                ],
                capture_output=True,
                text=True
            )

            repos = [r for r in result.stdout.strip().split('\n')
                     if r.startswith(f"{self.config.course_id}-{self.config.assignment_id}-")]

            for repo in repos:
                repo_path = self.config.submissions_dir / repo
                if not repo_path.exists():
                    subprocess.run([
                        "git", "clone",
                        f"https://github.com/{self.config.organization}/{repo}",
                        str(repo_path)
                    ], capture_output=True)
                    print(f"  Cloned: {repo}")
                else:
                    subprocess.run(
                        ["git", "pull"],
                        cwd=repo_path,
                        capture_output=True
                    )
                    print(f"  Updated: {repo}")

        # Count cloned repos
        repos = list(self.config.submissions_dir.iterdir())
        print(f"\nTotal repositories: {len(repos)}")
        return len(repos) > 0

    def step2_extract_visible_scores(self) -> Path:
        """Extract visible test scores."""
        print("\n" + "=" * 60)
        print("STEP 2: Extracting Visible Test Scores")
        print("=" * 60)

        output_file = self.config.grades_dir / f"{self.config.assignment_id}-visible-{self.config.timestamp}.csv"

        # Run batch grading script
        batch_script = self.scripts_dir / "batch_grade.sh"
        if batch_script.exists():
            result = subprocess.run(
                ["bash", str(batch_script), f"{self.config.course_id}-{self.config.assignment_id}"],
                cwd=self.config.grading_home,
                capture_output=True,
                text=True
            )
            print(result.stdout)

        # Export results
        export_script = self.scripts_dir / "export_grades.py"
        if export_script.exists():
            grades_dir = self.config.grading_home / "grades" / f"{self.config.course_id}-{self.config.assignment_id}"
            subprocess.run([
                sys.executable, str(export_script),
                f"{self.config.course_id}-{self.config.assignment_id}",
                str(grades_dir),
                str(output_file)
            ])

        print(f"Visible scores: {output_file}")
        return output_file

    def step3_run_hidden_tests(self) -> Path:
        """Run hidden tests on all submissions."""
        print("\n" + "=" * 60)
        print("STEP 3: Running Hidden Tests")
        print("=" * 60)

        output_file = self.config.grades_dir / f"{self.config.assignment_id}-hidden-{self.config.timestamp}.csv"

        hidden_test_script = self.scripts_dir / "run_hidden_tests.py"
        if hidden_test_script.exists():
            result = subprocess.run([
                sys.executable, str(hidden_test_script),
                "--hidden-tests", str(self.config.hidden_tests_repo),
                "--submissions", str(self.config.submissions_dir),
                "--assignment", self.config.assignment_id,
                "--course", self.config.course_id,
                "--output", str(output_file)
            ])
        else:
            print("Warning: run_hidden_tests.py not found")

        print(f"Hidden scores: {output_file}")
        return output_file

    def step4_plagiarism_check(self) -> Path:
        """Run plagiarism detection."""
        print("\n" + "=" * 60)
        print("STEP 4: Plagiarism Detection")
        print("=" * 60)

        output_file = self.config.reports_dir / "similarity_results.csv"

        # Try JPlag first
        jplag_script = self.scripts_dir / "run_jplag.sh"
        if jplag_script.exists():
            result = subprocess.run([
                "bash", str(jplag_script),
                f"{self.config.course_id}-{self.config.assignment_id}",
                "python",  # Default language
                str(self.config.reports_dir)
            ], capture_output=True, text=True)
            print(result.stdout)
        else:
            # Fallback to MOSS
            moss_script = self.scripts_dir / "run_moss.sh"
            if moss_script.exists():
                subprocess.run([
                    "bash", str(moss_script),
                    f"{self.config.course_id}-{self.config.assignment_id}",
                    "python"
                ], cwd=self.config.grading_home)

        print(f"Plagiarism report: {self.config.reports_dir}")
        return output_file

    def step5_calculate_final_grades(
        self,
        visible_file: Path,
        hidden_file: Path,
        plagiarism_file: Path
    ) -> Path:
        """Calculate final weighted grades."""
        print("\n" + "=" * 60)
        print("STEP 5: Calculating Final Grades")
        print("=" * 60)

        output_file = self.config.grades_dir / f"{self.config.assignment_id}-final-{self.config.timestamp}.csv"

        grade_calc_script = self.scripts_dir / "grade_calculator.py"
        if grade_calc_script.exists():
            cmd = [
                sys.executable, str(grade_calc_script),
                "--output", str(output_file)
            ]
            if visible_file.exists():
                cmd.extend(["--visible", str(visible_file)])
            if hidden_file.exists():
                cmd.extend(["--hidden", str(hidden_file)])
            if plagiarism_file.exists():
                cmd.extend(["--plagiarism", str(plagiarism_file)])

            subprocess.run(cmd)

        print(f"Final grades: {output_file}")
        return output_file

    def step6_export_for_lms(self, grades_file: Path) -> Path:
        """Export grades in LMS-compatible format."""
        print("\n" + "=" * 60)
        print("STEP 6: Exporting for LMS")
        print("=" * 60)

        output_file = self.config.grades_dir / f"{self.config.assignment_id}-lms-{self.config.timestamp}.csv"

        # Simple transformation for Moodle format
        import csv

        if grades_file.exists():
            with open(grades_file) as f_in, open(output_file, 'w', newline='') as f_out:
                reader = csv.DictReader(f_in)
                writer = csv.writer(f_out)

                # Moodle format
                writer.writerow(['identifier', 'grade', 'feedback'])

                for row in reader:
                    writer.writerow([
                        row.get('Student ID', row.get('student_id', '')),
                        row.get('Final Score', row.get('final_score', '')),
                        row.get('Comments', '')
                    ])

        print(f"LMS export: {output_file}")
        return output_file

    def run_full_pipeline(self, skip_clone: bool = False):
        """Execute the complete grading pipeline."""
        print("\n" + "=" * 60)
        print(f"GRADING PIPELINE: {self.config.course_id} - {self.config.assignment_id}")
        print(f"Timestamp: {self.config.timestamp}")
        print("=" * 60)

        # Step 1: Clone
        if not skip_clone:
            if not self.step1_clone_submissions():
                print("ERROR: No submissions found")
                return

        # Step 2: Visible tests
        visible_file = self.step2_extract_visible_scores()

        # Step 3: Hidden tests
        hidden_file = self.step3_run_hidden_tests()

        # Step 4: Plagiarism
        plagiarism_file = self.step4_plagiarism_check()

        # Step 5: Final grades
        final_grades = self.step5_calculate_final_grades(
            visible_file, hidden_file, plagiarism_file
        )

        # Step 6: LMS export
        lms_file = self.step6_export_for_lms(final_grades)

        # Summary
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Submissions: {self.config.submissions_dir}")
        print(f"Final grades: {final_grades}")
        print(f"LMS export: {lms_file}")
        print(f"Plagiarism report: {self.config.reports_dir}")


def main():
    parser = argparse.ArgumentParser(description="Run complete grading pipeline")
    parser.add_argument("--course", "-c", required=True, help="Course ID (e.g., csc3301)")
    parser.add_argument("--assignment", "-a", required=True, help="Assignment ID (e.g., lab01-scope-binding)")
    parser.add_argument("--grading-home", "-g", type=Path,
                        default=Path.home() / "course-grading",
                        help="Grading home directory")
    parser.add_argument("--hidden-tests", "-t", type=Path, help="Hidden tests repository path")
    parser.add_argument("--skip-clone", action="store_true", help="Skip cloning step")
    parser.add_argument("--org", default="unza-cs-courses", help="GitHub organization")

    args = parser.parse_args()

    config = PipelineConfig(
        course_id=args.course,
        assignment_id=args.assignment,
        grading_home=args.grading_home,
        organization=args.org,
        hidden_tests_repo=args.hidden_tests
    )

    pipeline = GradingPipeline(config)
    pipeline.run_full_pipeline(skip_clone=args.skip_clone)


if __name__ == "__main__":
    main()
