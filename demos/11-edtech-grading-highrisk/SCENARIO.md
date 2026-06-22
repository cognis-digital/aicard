# Demo 11 - Automated essay scoring (EdTech, high-risk)

**Where the data came from:** an EdTech vendor drafting an Annex IV technical
file for an automated essay scorer used in secondary-school assessment. AI used
to evaluate educational outcomes is **Annex III high-risk** under the EU AI Act.

**What to expect:** the descriptor is strong on governance, fairness, and human
oversight, but the team left `measure.test_data` empty. That is a **blocker**
(EU AI Act Annex IV 2(d) data & datasets), so `check` exits **1** and the CI
gate fails. Coverage score lands around **93.8%**.

## Run it

```bash
python -m aicard check demos/11-edtech-grading-highrisk/essay_grader.json
# emit SARIF for GitHub code-scanning on the technical file
python -m aicard check demos/11-edtech-grading-highrisk/essay_grader.json --format sarif > essay.sarif
```

## How to act

Fill in `measure.test_data` with a real description of the evaluation set
(size, source, label provenance, demographic stratification). Re-run; the
blocker clears and the gate goes green. Note the descriptor already flags an
ELL under-scoring gap in `measure.fairness` - act on that before deployment.
