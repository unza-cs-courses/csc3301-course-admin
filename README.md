# CSC3301 Course Administration

**Programming Language Paradigms — GitHub Classroom Setup**

This repository contains administrative scripts and documentation for managing the CSC3301 GitHub Classroom infrastructure.

---

## Repository Overview

| Repository | Type | Language | Description |
|------------|------|----------|-------------|
| `csc3301-lab01-scope-binding` | Lab | Python | Scope, binding, namespaces |
| `csc3301-lab02-type-systems` | Lab | Python | Type systems, mypy, type checker |
| `csc3301-lab03-functional-programming` | Lab | Python | HOFs, map/filter/reduce |
| `csc3301-lab04-oop-design` | Lab | Python | Design patterns, polymorphism |
| `csc3301-lab05-logic-programming` | Lab | Prolog | Facts, rules, backtracking |
| `csc3301-lab06-concurrency` | Lab | Python | Threading, async, multiprocessing |
| `csc3301-proj01-expression-evaluator` | Project | Python | Parser, AST, evaluator |
| `csc3301-proj02-symbolic-differentiator` | Project | Scheme | Symbolic math, recursion |
| `csc3301-proj03-design-patterns` | Project | Python | GoF patterns library |
| `csc3301-proj04-expert-system` | Project | Prolog | Knowledge base, inference |
| `csc3301-proj05-concurrent-pipeline` | Project | Python | Multi-paradigm integration |

---

## Quick Start

### 1. Push Template Repositories

```bash
# Clone this package
# Then run the push script with your token
./scripts/push_all_repos.sh YOUR_GITHUB_TOKEN
```

### 2. Create GitHub Classroom

1. Go to https://classroom.github.com
2. Create new classroom linked to `unza-cs-courses`
3. Name: `CSC3301 Programming Language Paradigms - 2026 Semester 1`

### 3. Create Assignments

For each template repo, create an assignment in GitHub Classroom:
- Link to template repository
- Set deadline
- Enable autograding
- Configure starter code

### 4. Import Roster

Upload CSV with columns: `identifier,email`

---

## Directory Structure

```
csc3301-course-admin/
├── scripts/
│   ├── push_all_repos.sh       # Push all templates to GitHub
│   ├── clone_submissions.sh    # Clone student submissions
│   ├── batch_grade.sh          # Run autograder on all repos
│   ├── run_moss.sh             # MOSS similarity detection
│   ├── run_jplag.sh            # JPlag similarity detection
│   └── export_grades.py        # Export to Moodle CSV
├── docs/
│   ├── instructor_guide.md     # Full instructor documentation
│   ├── student_onboarding.md   # Student setup guide
│   └── grading_workflow.md     # End-to-end grading process
└── templates/
    └── assignment_template.md  # Template for new assignments
```

---

## Scripts

### Push All Repositories
```bash
./scripts/push_all_repos.sh ghp_YourTokenHere
```

### Clone All Submissions
```bash
./scripts/clone_submissions.sh csc3301-lab01-scope-binding
```

### Run MOSS
```bash
./scripts/run_moss.sh project-1 python
```

### Export Grades
```bash
python scripts/export_grades.py project-1 ./grades moodle_export.csv
```

---

## Grading Workflow

1. **After Deadline:**
   ```bash
   ./scripts/clone_submissions.sh <assignment>
   ./scripts/batch_grade.sh <assignment>
   ```

2. **Similarity Check:**
   ```bash
   ./scripts/run_moss.sh <assignment> python
   ```

3. **Manual Review:** Use fast-marking checklist (5-7 min/student)

4. **Export:**
   ```bash
   python scripts/export_grades.py <assignment> ./grades output.csv
   ```

---

## Contact

- Course Coordinator: [TBD]
- Technical Support: [TBD]
