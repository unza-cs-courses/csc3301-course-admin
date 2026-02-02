#!/usr/bin/env python3
"""
Grade Calculator for CSC3301
Combines visible tests, hidden tests, and plagiarism scores into final grades.

Usage:
    python grade_calculator.py \
        --visible visible_results.csv \
        --hidden hidden_results.csv \
        --plagiarism jplag_results.csv \
        --output final_grades.csv
"""
import csv
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GradeRecord:
    """Complete grade record for a student."""
    student_id: str
    github_username: str = ""
    visible_score: float = 0.0
    hidden_score: float = 0.0
    code_quality_score: float = 100.0  # Default full marks, deduct manually
    plagiarism_similarity: float = 0.0
    plagiarism_flag: bool = False
    plagiarism_partner: str = ""
    final_score: float = 0.0
    letter_grade: str = ""
    comments: List[str] = field(default_factory=list)


class GradeCalculator:
    """Calculates final grades from multiple score sources."""

    # Default weights - can be overridden via config
    DEFAULT_WEIGHTS = {
        "visible_tests": 0.40,
        "hidden_tests": 0.30,
        "code_quality": 0.20,
        "participation": 0.10,  # Reserved for manual adjustment
    }

    # Plagiarism penalty thresholds
    PLAGIARISM_THRESHOLDS = {
        "warning": 40,      # Flag for review
        "penalty_start": 50,  # Start applying penalty
        "severe": 80,       # Maximum penalty
    }

    # Letter grade boundaries
    GRADE_BOUNDARIES = [
        (90, "A+"), (85, "A"), (80, "A-"),
        (75, "B+"), (70, "B"), (65, "B-"),
        (60, "C+"), (55, "C"), (50, "C-"),
        (45, "D+"), (40, "D"),
        (0, "F")
    ]

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with optional config file."""
        self.weights = self.DEFAULT_WEIGHTS.copy()
        self.grades: Dict[str, GradeRecord] = {}

        if config_path and config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                if "weights" in config:
                    self.weights.update(config["weights"])

    def load_visible_scores(self, csv_path: Path):
        """Load visible test scores from CSV."""
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                student_id = row.get('identifier') or row.get('student_id') or row.get('Student ID')
                score = float(row.get('grade') or row.get('score') or row.get('Visible Score') or 0)

                if student_id not in self.grades:
                    self.grades[student_id] = GradeRecord(student_id=student_id)

                self.grades[student_id].visible_score = score

    def load_hidden_scores(self, csv_path: Path):
        """Load hidden test scores from CSV."""
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                student_id = row.get('Student ID') or row.get('student_id')
                score = float(row.get('Hidden Score') or row.get('hidden_score') or 0)

                if student_id not in self.grades:
                    self.grades[student_id] = GradeRecord(student_id=student_id)

                self.grades[student_id].hidden_score = score
                self.grades[student_id].github_username = row.get('Repository', '').split('/')[-1]

    def load_plagiarism_results(self, csv_path: Path):
        """Load plagiarism detection results."""
        if not csv_path.exists():
            return

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle different CSV formats from JPlag/MOSS
                student1 = row.get('submission1') or row.get('Student 1') or row.get('first')
                student2 = row.get('submission2') or row.get('Student 2') or row.get('second')
                similarity = float(row.get('similarity') or row.get('Similarity') or row.get('percent') or 0)

                # Extract student IDs from submission names
                for sid, partner in [(student1, student2), (student2, student1)]:
                    # Extract username from repo name format
                    student_id = sid.split('-')[-1] if '-' in sid else sid

                    if student_id in self.grades:
                        current = self.grades[student_id].plagiarism_similarity
                        if similarity > current:
                            self.grades[student_id].plagiarism_similarity = similarity
                            self.grades[student_id].plagiarism_partner = partner

    def _calculate_plagiarism_penalty(self, similarity: float) -> float:
        """Calculate penalty factor based on similarity percentage."""
        if similarity < self.PLAGIARISM_THRESHOLDS["penalty_start"]:
            return 0.0

        if similarity >= self.PLAGIARISM_THRESHOLDS["severe"]:
            return 0.50  # 50% penalty for severe cases

        # Linear interpolation between penalty_start and severe
        start = self.PLAGIARISM_THRESHOLDS["penalty_start"]
        severe = self.PLAGIARISM_THRESHOLDS["severe"]
        penalty_range = 0.50  # Max penalty

        return ((similarity - start) / (severe - start)) * penalty_range

    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        for threshold, grade in self.GRADE_BOUNDARIES:
            if score >= threshold:
                return grade
        return "F"

    def calculate_final_grades(self):
        """Calculate final grades for all students."""
        for student_id, record in self.grades.items():
            # Calculate weighted base score
            base_score = (
                record.visible_score * self.weights["visible_tests"] +
                record.hidden_score * self.weights["hidden_tests"] +
                record.code_quality_score * self.weights["code_quality"]
            )

            # Apply plagiarism penalty
            if record.plagiarism_similarity >= self.PLAGIARISM_THRESHOLDS["warning"]:
                record.plagiarism_flag = True
                record.comments.append(
                    f"Plagiarism warning: {record.plagiarism_similarity:.0f}% "
                    f"similarity with {record.plagiarism_partner}"
                )

            penalty = self._calculate_plagiarism_penalty(record.plagiarism_similarity)
            if penalty > 0:
                record.final_score = base_score * (1 - penalty)
                record.comments.append(f"Plagiarism penalty: -{penalty*100:.0f}%")
            else:
                record.final_score = base_score

            # Assign letter grade
            record.letter_grade = self._get_letter_grade(record.final_score)

    def export_grades(self, output_path: Path):
        """Export final grades to CSV."""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Student ID', 'GitHub Username',
                'Visible Score', 'Hidden Score', 'Code Quality',
                'Plagiarism %', 'Plagiarism Flag',
                'Final Score', 'Letter Grade', 'Comments'
            ])

            for record in sorted(self.grades.values(), key=lambda x: x.student_id):
                writer.writerow([
                    record.student_id,
                    record.github_username,
                    f"{record.visible_score:.1f}",
                    f"{record.hidden_score:.1f}",
                    f"{record.code_quality_score:.1f}",
                    f"{record.plagiarism_similarity:.1f}",
                    "YES" if record.plagiarism_flag else "NO",
                    f"{record.final_score:.1f}",
                    record.letter_grade,
                    "; ".join(record.comments)
                ])

        print(f"Grades exported to: {output_path}")

    def print_summary(self):
        """Print grade distribution summary."""
        scores = [r.final_score for r in self.grades.values()]
        grades = [r.letter_grade for r in self.grades.values()]

        print("\n" + "=" * 50)
        print("GRADE SUMMARY")
        print("=" * 50)
        print(f"Total students: {len(self.grades)}")
        print(f"Average score: {sum(scores)/len(scores):.1f}%")
        print(f"Highest score: {max(scores):.1f}%")
        print(f"Lowest score: {min(scores):.1f}%")

        print("\nGrade Distribution:")
        for grade in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]:
            count = grades.count(grade)
            if count > 0:
                bar = "█" * count
                print(f"  {grade:3}: {bar} ({count})")

        flagged = sum(1 for r in self.grades.values() if r.plagiarism_flag)
        if flagged > 0:
            print(f"\nPlagiarism flags: {flagged}")


def main():
    parser = argparse.ArgumentParser(description="Calculate final grades")
    parser.add_argument("--visible", "-v", type=Path, help="Visible test scores CSV")
    parser.add_argument("--hidden", "-h", type=Path, help="Hidden test scores CSV")
    parser.add_argument("--plagiarism", "-p", type=Path, help="Plagiarism results CSV")
    parser.add_argument("--config", "-c", type=Path, help="Config file with weights")
    parser.add_argument("--output", "-o", type=Path, default=Path("final_grades.csv"))

    args = parser.parse_args()

    calculator = GradeCalculator(config_path=args.config)

    if args.visible:
        calculator.load_visible_scores(args.visible)
    if args.hidden:
        calculator.load_hidden_scores(args.hidden)
    if args.plagiarism:
        calculator.load_plagiarism_results(args.plagiarism)

    calculator.calculate_final_grades()
    calculator.export_grades(args.output)
    calculator.print_summary()


if __name__ == "__main__":
    main()
