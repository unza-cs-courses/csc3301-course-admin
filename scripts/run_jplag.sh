#!/bin/bash
# Run JPlag plagiarism detection
# Usage: ./run_jplag.sh <assignment> <language> [output_dir]
#
# Example:
#   ./run_jplag.sh csc3301-lab01-scope-binding python ./reports
#
# Languages: python3, java, cpp, javascript, scheme, text

set -e

ASSIGNMENT=$1
LANGUAGE=${2:-python3}
OUTPUT_DIR=${3:-"jplag_results/$ASSIGNMENT"}
SUBMISSIONS_DIR="submissions/$ASSIGNMENT"
JPLAG_JAR="${JPLAG_JAR:-$HOME/course-grading/tools/jplag.jar}"

# Check prerequisites
if [ -z "$ASSIGNMENT" ]; then
    echo "Usage: ./run_jplag.sh <assignment> [language] [output_dir]"
    echo "Languages: python3, java, cpp, javascript, scheme, text"
    exit 1
fi

if [ ! -f "$JPLAG_JAR" ]; then
    echo "Error: JPlag JAR not found at $JPLAG_JAR"
    echo "Download from: https://github.com/jplag/jplag/releases"
    echo "Set JPLAG_JAR environment variable or place in ~/course-grading/tools/"
    exit 1
fi

if [ ! -d "$SUBMISSIONS_DIR" ]; then
    echo "Error: Submissions directory not found: $SUBMISSIONS_DIR"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== JPlag Plagiarism Detection ==="
echo "Assignment: $ASSIGNMENT"
echo "Language: $LANGUAGE"
echo "Submissions: $SUBMISSIONS_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

# Map language names
case $LANGUAGE in
    python|python3|py)
        JPLAG_LANG="python3"
        FILE_SUFFIX="py"
        ;;
    java)
        JPLAG_LANG="java"
        FILE_SUFFIX="java"
        ;;
    cpp|c++)
        JPLAG_LANG="cpp"
        FILE_SUFFIX="cpp"
        ;;
    javascript|js)
        JPLAG_LANG="javascript"
        FILE_SUFFIX="js"
        ;;
    scheme|racket|rkt)
        JPLAG_LANG="scheme"
        FILE_SUFFIX="rkt"
        ;;
    prolog|pl)
        JPLAG_LANG="text"
        FILE_SUFFIX="pl"
        ;;
    *)
        JPLAG_LANG="$LANGUAGE"
        FILE_SUFFIX="*"
        ;;
esac

# Run JPlag
echo "Running JPlag analysis..."
java -jar "$JPLAG_JAR" \
    --language "$JPLAG_LANG" \
    --result-folder "$OUTPUT_DIR" \
    --similarity-threshold 30 \
    --shown-comparisons 100 \
    --subdirectory "src" \
    "$SUBMISSIONS_DIR"

# Check for results
if [ -f "$OUTPUT_DIR/results.json" ]; then
    echo ""
    echo "=== High Similarity Pairs ==="

    # Extract high similarity pairs using Python
    python3 << EOF
import json
import sys

try:
    with open("$OUTPUT_DIR/results.json") as f:
        data = json.load(f)

    comparisons = data.get('comparisons', [])

    # Sort by similarity
    comparisons.sort(key=lambda x: x.get('similarity', 0), reverse=True)

    # Show top pairs
    print(f"{'Submission 1':<30} {'Submission 2':<30} {'Similarity':>10}")
    print("-" * 72)

    high_similarity = []
    for comp in comparisons[:20]:
        sub1 = comp.get('firstSubmission', 'Unknown')
        sub2 = comp.get('secondSubmission', 'Unknown')
        sim = comp.get('similarity', 0) * 100

        # Extract student IDs
        id1 = sub1.split('-')[-1] if '-' in sub1 else sub1
        id2 = sub2.split('-')[-1] if '-' in sub2 else sub2

        print(f"{id1:<30} {id2:<30} {sim:>9.1f}%")

        if sim >= 50:
            high_similarity.append({
                'submission1': id1,
                'submission2': id2,
                'similarity': sim
            })

    # Export high similarity pairs to CSV
    if high_similarity:
        import csv
        with open("$OUTPUT_DIR/high_similarity.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['submission1', 'submission2', 'similarity'])
            writer.writeheader()
            writer.writerows(high_similarity)
        print(f"\nHigh similarity pairs exported to: $OUTPUT_DIR/high_similarity.csv")

except Exception as e:
    print(f"Error parsing results: {e}", file=sys.stderr)
EOF

fi

echo ""
echo "=== Complete ==="
echo "Report: $OUTPUT_DIR/index.html"
echo ""
echo "To view the report:"
echo "  open $OUTPUT_DIR/index.html"
