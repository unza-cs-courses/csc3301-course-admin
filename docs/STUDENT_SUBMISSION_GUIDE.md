# CSC3301 Student Submission Guide

**Course:** CSC3301 Programming Language Paradigms  
**University of Zambia**  
**Last Updated:** February 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Accepting an Assignment](#step-1-accepting-an-assignment)
4. [Step 2: Understanding Your Personalized Assignment](#step-2-understanding-your-personalized-assignment)
5. [Step 3: Working on Your Assignment](#step-3-working-on-your-assignment)
6. [Step 4: Testing Your Code Locally](#step-4-testing-your-code-locally)
7. [Step 5: Submitting Your Work](#step-5-submitting-your-work)
8. [Step 6: Checking Autograder Feedback](#step-6-checking-autograder-feedback)
9. [Step 7: Understanding Your Grade](#step-7-understanding-your-grade)
10. [Troubleshooting](#troubleshooting)
11. [Academic Integrity](#academic-integrity)

---

## Overview

This guide walks you through the complete process of completing and submitting assignments in CSC3301. Our course uses **GitHub Classroom** for assignment distribution and automated grading.

### Key Features of Our System

- **Personalized Variants**: Each student receives a unique version of each assignment
- **Automated Testing**: Your code is tested automatically when you push
- **Immediate Feedback**: See your visible test results within minutes
- **Hidden Tests**: Additional tests are run during final grading
- **Plagiarism Detection**: All submissions are checked for similarity

---

## Prerequisites

Before starting any assignment, ensure you have:

### Required Software

1. **Git** - Version control system
   ```bash
   # Check if installed
   git --version
   
   # Install on Ubuntu/Debian
   sudo apt install git
   
   # Install on macOS
   brew install git
   ```

2. **Python 3.11+** - For Python-based assignments
   ```bash
   # Check version
   python3 --version
   
   # Should be 3.11 or higher
   ```

3. **Required Python packages**
   ```bash
   pip install pytest mypy flake8
   ```

### GitHub Account

1. Create a GitHub account at [github.com](https://github.com) if you don't have one
2. Use your university email or add it to your GitHub account
3. **Important**: Your GitHub username will be associated with your submissions

### Git Configuration

```bash
# Set your name and email
git config --global user.name "Your Full Name"
git config --global user.email "your.email@unza.zm"
```

---

## Step 1: Accepting an Assignment

### 1.1 Find the Assignment Link

Your instructor will share a GitHub Classroom link for each assignment. It looks like:
```
https://classroom.github.com/a/XXXXXXX
```

### 1.2 Accept the Assignment

1. Click the assignment link
2. Sign in to GitHub if prompted
3. Click **"Accept this assignment"**
4. Wait for GitHub to create your repository

![Accept Assignment](images/accept-assignment.png)

### 1.3 Repository Created

After accepting, you'll see a confirmation page with:
- Your unique repository URL
- A link to your new repository

Your repository will be named:
```
csc3301-[assignment-name]-[your-github-username]
```

For example: `csc3301-lab02-type-systems-mofya`

### 1.4 Clone Your Repository

```bash
# Clone your repository
git clone https://github.com/unza-cs-courses/csc3301-lab02-type-systems-mofya.git

# Navigate into the directory
cd csc3301-lab02-type-systems-mofya
```

---

## Step 2: Understanding Your Personalized Assignment

### 2.1 Automatic Variant Generation

When you first push to your repository (or when the repo is created), GitHub Actions automatically:

1. Extracts your student ID from the repository name
2. Generates a unique `.variant_config.json` file
3. Creates a personalized `ASSIGNMENT.md` file

### 2.2 Check Your Assignment

After the variant generation completes:

```bash
# Pull the generated files
git pull

# View your personalized assignment
cat ASSIGNMENT.md
```

### 2.3 Understanding Your Variant

Open `.variant_config.json` to see your unique configuration:

```json
{
  "student_id": "mofya",
  "seed": 1290806332,
  "python_coercions": [...],
  "javascript_coercions": [...],
  "c_coercions": [...],
  "type_check_tests": [...]
}
```

**Important**: 
- Your variant is deterministic based on your student ID
- Do NOT share your variant with other students
- The tests are customized to YOUR variant

---

## Step 3: Working on Your Assignment

### 3.1 Read the Assignment Carefully

Your `ASSIGNMENT.md` file contains:
- Task descriptions
- Your specific test cases/examples
- Grading rubric
- Submission checklist

### 3.2 File Structure

Typical assignment structure:
```
csc3301-lab02-type-systems-mofya/
├── .github/
│   └── workflows/           # GitHub Actions (do not modify)
├── scripts/                 # Utility scripts (do not modify)
├── src/
│   ├── __init__.py
│   ├── task1_annotations.py # Your code goes here
│   └── task2_type_checker.py
├── tests/
│   └── visible/
│       ├── conftest.py      # Test configuration
│       └── test_lab2.py     # Visible tests
├── .variant_config.json     # Your variant (do not modify)
├── ASSIGNMENT.md            # Your personalized assignment
└── SUBMISSION.md            # Fill this out before submitting
```

### 3.3 Completing Tasks

For each task in your assignment:

1. **Read the requirements** in `ASSIGNMENT.md`
2. **Open the source file** in `src/`
3. **Implement the required functionality**
4. **Test locally** before pushing

#### Example: Task 1 - Type Annotations

Original code in `src/task1_annotations.py`:
```python
# TODO: Add type hints
def find_max(numbers):
    if not numbers:
        return None
    return max(numbers)
```

Your solution:
```python
from typing import Optional

def find_max(numbers: list[float]) -> Optional[float]:
    """Find the maximum value in a list of numbers."""
    if not numbers:
        return None
    return max(numbers)
```

---

## Step 4: Testing Your Code Locally

### 4.1 Run Visible Tests

```bash
# Run all visible tests
pytest tests/visible/ -v

# Run tests with detailed output
pytest tests/visible/ -v --tb=short
```

Expected output for passing tests:
```
============================= test session starts ==============================
tests/visible/test_lab2.py::TestTask1Annotations::test_mypy_passes PASSED [ 20%]
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_literal PASSED [ 40%]
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_addition PASSED [ 60%]
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_float_addition PASSED [ 80%]
tests/visible/test_lab2.py::TestTask2TypeChecker::test_type_error PASSED [100%]
============================== 5 passed in 1.55s ===============================
```

### 4.2 Check Type Annotations (for type-related assignments)

```bash
# Run mypy in strict mode
mypy src/task1_annotations.py --strict
```

Expected output:
```
Success: no issues found in 1 source file
```

### 4.3 Check Code Style

```bash
# Run flake8 for style checking
flake8 src/ --max-line-length=100
```

### 4.4 Common Testing Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Make sure you're in the repo root directory |
| `ImportError` | Check that `__init__.py` files exist |
| Tests fail locally but pass on GitHub | Ensure you have Python 3.11+ |

---

## Step 5: Submitting Your Work

### 5.1 Complete the Submission Checklist

Before submitting, open `SUBMISSION.md` and:
1. Fill in your student ID and name
2. Write your reflection (5-10 sentences)
3. Check off completed items

### 5.2 Stage Your Changes

```bash
# Check what files have changed
git status

# Stage all changes
git add .

# Or stage specific files
git add src/task1_annotations.py src/task2_type_checker.py SUBMISSION.md
```

### 5.3 Commit Your Work

```bash
# Commit with a meaningful message
git commit -m "Complete Lab 2: Type Systems

- Add type annotations to ShoppingCart class
- Implement type_check function for expression AST
- Complete reflection in SUBMISSION.md"
```

### 5.4 Push to GitHub

```bash
# Push to your repository
git push origin main
```

### 5.5 Verify Your Submission

1. Go to your repository on GitHub
2. Check that all files are updated
3. Wait for the autograder to run (1-2 minutes)

---

## Step 6: Checking Autograder Feedback

### 6.1 View GitHub Actions

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. Click on the latest workflow run

![GitHub Actions](images/github-actions.png)

### 6.2 Understanding the Workflow

The autograder runs several steps:

1. **Setup Python** - Configures the environment
2. **Install Dependencies** - Installs pytest, mypy, etc.
3. **Check Variant** - Verifies your variant configuration
4. **Run Visible Tests** - Runs tests you can see
5. **Run Type Checking** - Checks type annotations (if applicable)

### 6.3 Reading Test Results

Click on **"Run Visible Tests"** to see detailed output:

```
============================= test session starts ==============================
tests/visible/test_lab2.py::TestTask1Annotations::test_mypy_passes PASSED
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_literal PASSED
...
============================== 5 passed in 1.55s ===============================
```

### 6.4 If Tests Fail

1. Read the error message carefully
2. The failing test shows:
   - What was expected
   - What your code produced
   - The line that failed
3. Fix the issue locally
4. Push again to re-run tests

Example failure:
```
FAILED tests/visible/test_lab2.py::test_type_error
    assert isinstance(type_check(expr), TypeError_)
    AssertionError: Expected TypeError_, got IntType
```

---

## Step 7: Understanding Your Grade

### 7.1 Grade Components

| Component | Weight | Description |
|-----------|--------|-------------|
| Visible Tests | 40% | Tests you can see and run locally |
| Hidden Tests | 30% | Additional tests run during grading |
| Code Quality | 20% | Style, documentation, design |
| Participation | 10% | Submission timeliness, reflection |

### 7.2 Hidden Tests

After the deadline, instructors run additional "hidden" tests that:
- Test edge cases you may not have considered
- Verify your code works with your specific variant
- Check for proper error handling

### 7.3 Plagiarism Detection

All submissions are automatically checked for similarity using:
- **JPlag** - Detects structural similarity
- **MOSS** - Stanford's plagiarism detection system

Thresholds:
- **< 40%**: Normal (common patterns/libraries)
- **40-50%**: Warning - reviewed by instructor
- **> 50%**: Flagged - potential academic misconduct

### 7.4 Grade Report

After grading, you'll receive a report through the course LMS that includes:
- Your final score and letter grade
- Feedback on your submission
- Any areas for improvement

Grades are typically released within one week of the assignment deadline.

---

## Troubleshooting

### Git Issues

**Problem**: `Permission denied` when pushing
```bash
# Solution: Use SSH or update credentials
git remote set-url origin git@github.com:unza-cs-courses/your-repo.git
```

**Problem**: Merge conflicts
```bash
# Pull and resolve conflicts
git pull --rebase origin main
# Edit conflicting files
git add .
git rebase --continue
git push
```

### Test Failures

**Problem**: Tests pass locally but fail on GitHub
- Check Python version (should be 3.11+)
- Ensure all dependencies are available
- Check if you're importing from correct paths

**Problem**: `ImportError: cannot import name 'X'`
```bash
# Make sure you're in the repo root
cd csc3301-lab02-type-systems-mofya
pytest tests/visible/ -v
```

### Variant Issues

**Problem**: `.variant_config.json` is missing
```bash
# Pull the latest changes
git pull origin main
# If still missing, the workflow may have failed - check Actions tab
```

**Problem**: Assignment shows template placeholders
- The variant generation workflow may not have run
- Check the Actions tab for errors
- Contact the instructor if the issue persists

---

## Academic Integrity

### What IS Allowed

✅ Discussing concepts with classmates  
✅ Using official documentation and textbooks  
✅ Asking the instructor for clarification  
✅ Using online resources to understand concepts  
✅ Getting help from tutors on general approaches  

### What is NOT Allowed

❌ Copying code from another student  
❌ Sharing your code with other students  
❌ Using AI to generate complete solutions  
❌ Submitting work that is not your own  
❌ Sharing your variant configuration  

### Consequences

First offense: Zero on the assignment + warning  
Second offense: Fail the course + disciplinary hearing

### Why We Use Variants

Each student receives unique test cases to:
1. Ensure you understand the concepts (not just copy solutions)
2. Make it impossible to simply share answers
3. Provide fair assessment for all students

---

## Getting Help

### Office Hours
- **When**: Tuesdays 2-4 PM, Thursdays 10 AM-12 PM
- **Where**: Computer Science Building, Room 305
- **Virtual**: Zoom link in course announcements

### Discussion Forum
- Post questions on the course forum
- Help your classmates (without sharing code!)
- Instructors monitor and respond daily

### Email
- For private matters: instructor@unza.zm
- Include your student ID and repository link

---

## Quick Reference

### Common Commands

```bash
# Clone repository
git clone https://github.com/unza-cs-courses/csc3301-lab02-type-systems-USERNAME.git

# Navigate to repo
cd csc3301-lab02-type-systems-USERNAME

# Pull latest changes (including variant)
git pull

# Run visible tests
pytest tests/visible/ -v

# Run mypy (for type assignments)
mypy src/task1_annotations.py --strict

# Stage, commit, and push
git add .
git commit -m "Your commit message"
git push
```

### Important Links

- GitHub Classroom: [classroom.github.com](https://classroom.github.com)
- Course Repository: [github.com/unza-cs-courses](https://github.com/unza-cs-courses)
- Python Documentation: [docs.python.org](https://docs.python.org)
- Typing Module: [docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)

---

## End-to-End Example: Student "mofya"

This section shows a complete submission workflow using a real example.

### Step 1: Accept Assignment
```
Repository created: csc3301-lab02-type-systems-mofya
```

### Step 2: Clone and View Variant
```bash
git clone https://github.com/unza-cs-courses/csc3301-lab02-type-systems-mofya.git
cd csc3301-lab02-type-systems-mofya
git pull  # Get generated variant files
```

Variant configuration generated:
```json
{
  "student_id": "mofya",
  "seed": 1290806332,
  "type_check_tests": [
    {"id": "tc_division", "expression": "BinOp('/', IntLit(28), IntLit(11))", ...},
    {"id": "tc_if_expr_int", ...},
    ...
  ]
}
```

### Step 3: Complete Assignment
Implemented solutions in:
- `src/task1_annotations.py` - Added type hints
- `src/task2_type_checker.py` - Implemented type_check()

### Step 4: Test Locally
```bash
$ pytest tests/visible/ -v
============================= test session starts ==============================
tests/visible/test_lab2.py::TestTask1Annotations::test_mypy_passes PASSED
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_literal PASSED
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_addition PASSED
tests/visible/test_lab2.py::TestTask2TypeChecker::test_int_float_addition PASSED
tests/visible/test_lab2.py::TestTask2TypeChecker::test_type_error PASSED
============================== 5 passed in 1.55s ===============================

$ mypy src/task1_annotations.py --strict
Success: no issues found in 1 source file
```

### Step 5: Submit
```bash
git add .
git commit -m "Complete Lab 2: Type Systems"
git push
```

### Step 6: Check Autograder
GitHub Actions shows: ✅ All checks passed

### Step 7: Final Grade
After the deadline, you'll receive your grade report via the course LMS with your final score and feedback.

---

*This guide is maintained by the CSC3301 teaching team. Last updated: February 2026*
