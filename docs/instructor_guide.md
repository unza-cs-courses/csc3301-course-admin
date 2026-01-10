# CSC3301 Instructor Guide

## Semester Setup Checklist

- [ ] Push all template repos to GitHub
- [ ] Create GitHub Classroom
- [ ] Import student roster
- [ ] Create assignments in Classroom
- [ ] Post assignment links to Moodle
- [ ] Set up MOSS account (email moss@moss.stanford.edu)

## Weekly Workflow

### Before Lab/Project Release
1. Verify template repo is ready
2. Create assignment in GitHub Classroom
3. Post announcement + link on Moodle

### After Deadline
1. Clone submissions: `./scripts/clone_submissions.sh <assignment>`
2. Run autograder: `./scripts/batch_grade.sh <assignment>`
3. Run similarity check: `./scripts/run_moss.sh <assignment> python`
4. Review flagged submissions (>50% similarity)
5. Complete manual review (~7 min/student)
6. Export grades: `python scripts/export_grades.py ...`
7. Upload to Moodle

## Similarity Triage

| % | Priority | Action |
|---|----------|--------|
| >80% | Critical | Interview both students |
| 60-80% | High | Review commit history |
| 40-60% | Medium | Check variant compliance |
| <40% | Normal | No action |
