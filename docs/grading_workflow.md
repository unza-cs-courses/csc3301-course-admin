# CSC3301 Grading Workflow

Complete guide for grading assignments from submission to LMS upload.

---

## Overview

```
Student Submits → Clone Repos → Run Tests → Plagiarism Check → Calculate Grades → Export to LMS
                     ↓              ↓              ↓                  ↓
                 GitHub         Visible +      JPlag/MOSS        Weighted
                Classroom       Hidden                           Combination
```

---

## Prerequisites

Before grading, ensure:

1. **Local environment is set up:**
   ```bash
   source ~/course-grading/activate.sh
   ```

2. **Hidden tests repository is cloned:**
   ```bash
   git -C ~/course-grading/hidden-tests pull
   ```

3. **Assignment deadline has passed**

---

## Quick Grading (One Command)

For most assignments, use the full pipeline:

```bash
python scripts/full_grading_pipeline.py \
    --course csc3301 \
    --assignment lab01-scope-binding
```

This runs all steps automatically.

---

## Manual Step-by-Step Process

### Step 1: Clone Submissions

```bash
./scripts/clone_submissions.sh csc3301-lab01-scope-binding
```

**Output:** `~/course-grading/submissions/csc3301-lab01-scope-binding/`

**Verify:**
```bash
ls submissions/csc3301-lab01-scope-binding | wc -l
# Should show number of submissions
```

---

### Step 2: Run Visible Tests

If not already extracted from GitHub Actions:

```bash
./scripts/batch_grade.sh csc3301-lab01-scope-binding
```

**Output:** Individual JSON files in `grades/csc3301-lab01-scope-binding/`

**Export to CSV:**
```bash
python scripts/export_grades.py \
    csc3301-lab01-scope-binding \
    grades/csc3301-lab01-scope-binding \
    grades/lab01-visible.csv
```

---

### Step 3: Run Hidden Tests

```bash
python scripts/run_hidden_tests.py \
    --hidden-tests ~/course-grading/hidden-tests \
    --submissions ~/course-grading/submissions/csc3301-lab01-scope-binding \
    --assignment lab01-scope-binding \
    --output grades/lab01-hidden.csv
```

**Expected output:**
```
[1/45] Testing: lab01-scope-binding-john_doe
  ✓ Score: 85.0% (17/20)
[2/45] Testing: lab01-scope-binding-jane_smith
  ✓ Score: 90.0% (18/20)
...
```

---

### Step 4: Plagiarism Detection

**Using JPlag (Recommended):**
```bash
./scripts/run_jplag.sh csc3301-lab01-scope-binding python
```

**Using MOSS (Alternative):**
```bash
./scripts/run_moss.sh csc3301-lab01-scope-binding python
```

**Review results:**
- JPlag: Open `jplag_results/csc3301-lab01-scope-binding/index.html`
- Check `high_similarity.csv` for flagged pairs

---

### Step 5: Calculate Final Grades

```bash
python scripts/grade_calculator.py \
    --visible grades/lab01-visible.csv \
    --hidden grades/lab01-hidden.csv \
    --plagiarism jplag_results/csc3301-lab01-scope-binding/high_similarity.csv \
    --output grades/lab01-final.csv
```

**Output includes:**
- Weighted final score
- Letter grade
- Plagiarism flags
- Comments

---

### Step 6: Manual Review (if needed)

For flagged submissions, review:

1. **Plagiarism pairs (>50% similarity):**
   - Check commit history for independent work
   - Review coding style differences
   - Interview students if necessary

2. **Code quality issues:**
   - Adjust `code_quality` score in final CSV
   - Add comments for feedback

---

### Step 7: Export to LMS

The final grades CSV is already in Moodle-compatible format:

| identifier | grade | feedback |
|------------|-------|----------|
| john_doe   | 85.5  | Passed 17/20 hidden tests |

**Upload to Moodle:**
1. Go to Course → Grades → Import
2. Select CSV file
3. Map columns: identifier → Username, grade → Grade

---

## Handling Special Cases

### Late Submissions

1. Set deadline in GitHub Classroom
2. Late submissions show in Actions tab
3. Apply late penalty manually in final CSV

### Regrade Requests

1. Pull latest from student's repo
2. Re-run hidden tests on specific submission:
   ```bash
   python scripts/run_hidden_tests.py \
       --submissions submissions/csc3301-lab01-scope-binding/lab01-scope-binding-student_name \
       ...
   ```
3. Update final grades CSV

### Variant Issues

If a student's variant wasn't generated:

1. Check `.variant_config.json` exists in their repo
2. If missing, generate manually:
   ```bash
   cd submissions/csc3301-lab01-scope-binding/lab01-scope-binding-username
   python scripts/variant_generator.py username
   ```
3. Re-run tests

---

## Troubleshooting

### Hidden tests fail to run

```
Error: No src/ directory found
```
→ Student didn't follow submission structure. Score as 0 or provide extension.

### JPlag memory error

```
java.lang.OutOfMemoryError
```
→ Increase Java heap: `java -Xmx4g -jar jplag.jar ...`

### Variant mismatch

Tests expect different values than student code produces.
→ Verify `.variant_config.json` matches test expectations.

---

## Timeline Template

| Day | Task |
|-----|------|
| D+0 | Deadline passes, clone submissions |
| D+1 | Run visible + hidden tests |
| D+2 | Run plagiarism check, review flags |
| D+3 | Calculate final grades |
| D+4 | Address regrade requests |
| D+5 | Upload to LMS |

---

## Grade Components Reference

| Component | Weight | Source | When |
|-----------|--------|--------|------|
| Visible Tests | 40% | GitHub Actions | Every push |
| Hidden Tests | 30% | Local machine | After deadline |
| Code Quality | 20% | Manual review | After deadline |
| Participation | 10% | Reserved | End of semester |

---

## Contact

- Technical issues: [Course Admin]
- Grading disputes: [Course Coordinator]
