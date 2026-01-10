#!/bin/bash
# Run autograder on all submissions
# Usage: ./batch_grade.sh <assignment>

ASSIGNMENT=$1
SUBMISSIONS_DIR="submissions/$ASSIGNMENT"
GRADES_DIR="grades/$ASSIGNMENT"

mkdir -p $GRADES_DIR

for repo in $SUBMISSIONS_DIR/*/; do
    STUDENT=$(basename $repo | rev | cut -d'-' -f1 | rev)
    echo "Grading: $STUDENT"
    
    cd $repo
    
    # Install deps and run tests
    pip install -r requirements.txt -q 2>/dev/null || true
    pytest tests/ --json-report --json-report-file=results.json -q 2>/dev/null || true
    
    # Copy results
    cp results.json "../../$GRADES_DIR/${STUDENT}.json" 2>/dev/null || true
    
    cd - > /dev/null
done

echo "Grades saved to: $GRADES_DIR/"
