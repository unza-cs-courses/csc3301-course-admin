#!/bin/bash
# Push all template repositories to GitHub
# Usage: ./push_all_repos.sh YOUR_GITHUB_TOKEN

set -e

TOKEN=$1
ORG="unza-cs-courses"

if [ -z "$TOKEN" ]; then
    echo "Usage: ./push_all_repos.sh YOUR_GITHUB_TOKEN"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGE_DIR="$(dirname "$SCRIPT_DIR")/.."

REPOS=(
    "csc3301-lab01-scope-binding"
    "csc3301-lab02-type-systems"
    "csc3301-lab03-functional-programming"
    "csc3301-lab04-oop-design"
    "csc3301-lab05-logic-programming"
    "csc3301-lab06-concurrency"
    "csc3301-proj01-expression-evaluator"
    "csc3301-proj02-symbolic-differentiator"
    "csc3301-proj03-design-patterns"
    "csc3301-proj04-expert-system"
    "csc3301-proj05-concurrent-pipeline"
    "csc3301-course-admin"
)

for repo in "${REPOS[@]}"; do
    echo "=========================================="
    echo "Processing: $repo"
    echo "=========================================="
    
    REPO_PATH="$PACKAGE_DIR/$repo"
    
    if [ ! -d "$REPO_PATH" ]; then
        echo "Directory not found: $REPO_PATH"
        continue
    fi
    
    cd "$REPO_PATH"
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        git init
        git branch -M main
    fi
    
    # Create repo on GitHub
    echo "Creating repo on GitHub..."
    curl -s -X POST \
        -H "Authorization: token $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/orgs/$ORG/repos" \
        -d "{\"name\":\"$repo\",\"private\":false,\"is_template\":true}" \
        > /dev/null
    
    # Add all files and push
    git add -A
    git commit -m "Initial commit: $repo template" 2>/dev/null || true
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://$TOKEN@github.com/$ORG/$repo.git"
    git push -u origin main --force
    
    echo "✓ $repo pushed successfully"
    echo ""
done

echo "=========================================="
echo "All repositories pushed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Go to https://classroom.github.com"
echo "2. Create assignments linking to these templates"
echo "3. IMPORTANT: Revoke the token used here"
