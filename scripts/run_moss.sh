#!/bin/bash
# Run MOSS similarity detection
# Usage: ./run_moss.sh <assignment> <language>

ASSIGNMENT=$1
LANGUAGE=$2
SUBMISSIONS_DIR="submissions/$ASSIGNMENT"
OUTPUT_DIR="moss_results/$ASSIGNMENT"

mkdir -p $OUTPUT_DIR moss_temp

echo "Collecting files..."
for repo in $SUBMISSIONS_DIR/*/; do
    STUDENT=$(basename $repo | rev | cut -d'-' -f1 | rev)
    
    if [ "$LANGUAGE" = "python" ]; then
        find "$repo/src" -name "*.py" -exec cp {} "moss_temp/${STUDENT}_" \; 2>/dev/null || true
    elif [ "$LANGUAGE" = "scheme" ]; then
        find "$repo/src" -name "*.rkt" -exec cp {} "moss_temp/${STUDENT}_" \; 2>/dev/null || true
    elif [ "$LANGUAGE" = "prolog" ]; then
        find "$repo/src" -name "*.pl" -exec cp {} "moss_temp/${STUDENT}_" \; 2>/dev/null || true
    fi
done

echo "Running MOSS..."
./moss.pl -l $LANGUAGE moss_temp/* | tee $OUTPUT_DIR/moss_output.txt

MOSS_URL=$(grep "http://moss.stanford.edu" $OUTPUT_DIR/moss_output.txt | tail -1)
echo "$MOSS_URL" > $OUTPUT_DIR/moss_url.txt

rm -rf moss_temp
echo "Results: $MOSS_URL"
