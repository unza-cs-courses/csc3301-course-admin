#!/bin/bash
# Clone all student submissions for an assignment
# Usage: ./clone_submissions.sh <assignment-prefix>

ASSIGNMENT=$1
ORG="unza-cs-courses"

if [ -z "$ASSIGNMENT" ]; then
    echo "Usage: ./clone_submissions.sh <assignment-prefix>"
    echo "Example: ./clone_submissions.sh csc3301-lab01-scope-binding"
    exit 1
fi

mkdir -p submissions/$ASSIGNMENT

echo "Cloning submissions for $ASSIGNMENT..."
gh repo list $ORG --json name --jq '.[] | .name' | grep "^${ASSIGNMENT}-" | while read repo; do
    echo "Cloning $repo..."
    git clone "https://github.com/$ORG/$repo" "submissions/$ASSIGNMENT/$repo" 2>/dev/null || \
    git -C "submissions/$ASSIGNMENT/$repo" pull
done

echo "Done! Submissions in: submissions/$ASSIGNMENT/"
