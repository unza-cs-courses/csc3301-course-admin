#!/usr/bin/env python3
"""Export grades to Moodle-compatible CSV."""
import json
import csv
import sys
from pathlib import Path

def export_grades(assignment, grades_dir, output_file):
    grades = []
    
    for score_file in Path(grades_dir).glob('*.json'):
        student_id = score_file.stem
        try:
            with open(score_file) as f:
                data = json.load(f)
            
            # Calculate score from pytest results
            tests = data.get('tests', [])
            passed = sum(1 for t in tests if t.get('outcome') == 'passed')
            total = len(tests)
            score = (passed / max(total, 1)) * 100
            
            grades.append({
                'identifier': student_id,
                'grade': round(score, 1),
                'feedback': f'Passed {passed}/{total} tests'
            })
        except Exception as e:
            print(f"Error processing {student_id}: {e}")
    
    # Write CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['identifier', 'grade', 'feedback'])
        writer.writeheader()
        writer.writerows(sorted(grades, key=lambda x: x['identifier']))
    
    print(f"Exported {len(grades)} grades to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python export_grades.py <assignment> <grades_dir> <output.csv>")
        sys.exit(1)
    export_grades(sys.argv[1], sys.argv[2], sys.argv[3])
