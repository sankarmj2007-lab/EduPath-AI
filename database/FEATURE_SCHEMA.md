# EduPath AI - Student Profile Feature Schema (v1)

One row = one student. These columns are also the fields the new profile form
should collect, so the dataset, the form and the ML model all stay in sync.

| Group | Columns | Type | Form field |
|---|---|---|---|
| ID | `student_id` | text | (not asked) |
| Basic | `education_stage`, `degree`, `department`, `study_year` | category / int | Step 1 |
| Academics | `cgpa` | float 5.0-10 | Step 2 |
| Skills | `skill_*` (one column per skill) | 0 none, 1 beginner, 2 intermediate, 3 advanced | Step 3: skill chips + level |
| Interests | `interest_*` | 0 / 1 | Step 4 |
| Preference | `pref_hardware_vs_software` | 1 (software) - 5 (hardware) | Step 4 |
| Assessment | `assessment_logical`, `assessment_math`, `assessment_programming`, `assessment_electronics` | 0-100 | Short AI assessment |
| Experience | `projects_count`, `internships_count`, `certifications_count` | int | Step 2 |
| Study habits | `weekly_study_hours`, `learning_style` | int / category | Step 5 |
| **Label** | `career` | one of 30 careers | predicted by the model |

## Notes
- `Target Career` from the old form is NOT a feature. It is optional
  ("Not sure - let AI decide") and must never be used to predict itself.
- Skill names come from `careers_dataset.csv` (`OOP` is merged into
  `Object-Oriented Programming`). Align them with `skills_dataset.csv`
  when the model is connected to the skill-gap module.
- Dataset is **synthetic** (see `generate_student_profiles.py`): similar careers
  overlap on purpose and ~13% of labels are noisy. Validate on real student
  responses before quoting accuracy.

## Baseline check (RandomForest, 80/20 stratified split, 3000 rows)
- Top-1 accuracy: 0.43
- Top-3 accuracy: 0.77

Top-3 matters most: the platform shows the 3 best careers. A model can only
beat this baseline honestly by using better features, not by tuning on test data.
