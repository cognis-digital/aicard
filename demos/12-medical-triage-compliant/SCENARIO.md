# Demo 12 - Clinical symptom-triage router (fully compliant)

**Where the data came from:** a hospital's clinical-AI safety board prepared
this descriptor for a nurse-facing telehealth triage assistant. Clinical
decision support is high-risk; the system is deliberately kept human-in-the-loop
and never patient-facing.

**What to expect:** every catalogued disclosure is present and substantive, so
`check` reports **100% coverage, 0 blockers, 0 warnings** and exits **0**. The
generated card is a deployable Annex IV-style technical file.

## Run it

```bash
python -m aicard check demos/12-medical-triage-compliant/symptom_triage.json
python -m aicard card  demos/12-medical-triage-compliant/symptom_triage.json
python -m aicard check demos/12-medical-triage-compliant/symptom_triage.json --format csv
```

## How to act

This is a worked example of a compliant high-risk medical descriptor: note the
conservative-bias mitigation, the under-triage surveillance in
`manage.monitoring`, and the explicit out-of-scope (no pediatric < 2y, no
autonomous diagnosis). Reuse this pattern for other clinical-support models.
