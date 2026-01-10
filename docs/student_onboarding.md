# CSC3301 Student Setup Guide

## Prerequisites

1. **GitHub Account**: Create at https://github.com if you don't have one
2. **Git**: Install from https://git-scm.com
3. **Python 3.11+**: Install from https://python.org
4. **VS Code** (recommended): Install from https://code.visualstudio.com

## Accepting an Assignment

1. Click the assignment link on Moodle
2. Authorize GitHub Classroom (first time only)
3. Select your student ID from the roster
4. Wait for repository to be created
5. Clone your repository:
   ```bash
   git clone https://github.com/unza-cs-courses/assignment-name-yourid
   ```

## Working on Assignments

```bash
# Make changes
# Then commit and push:
git add .
git commit -m "Describe your changes"
git push

# Check autograder results on GitHub Actions tab
```

## Submitting Milestones

```bash
git tag milestone-1
git push --tags
```

## Getting Help

- Check GitHub Actions tab for autograder feedback
- Post questions on Moodle discussion
- Attend office hours
