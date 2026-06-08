# Demo 01 - Basic compliance check & model card

This scenario shows AICARD evaluating a real-ish AI system descriptor and
emitting both a compliance report and a model card.

The descriptor `loan_triage.json` documents a (deliberately *incomplete*)
high-risk credit-scoring assistant. It is missing a couple of disclosures so
you can see AICARD's findings and non-zero exit behaviour - exactly what you'd
wire into CI to block an under-documented model from shipping.

## Run it

```bash
# Compliance report (human-readable table)
python -m aicard check demos/01-basic/loan_triage.json

# Machine-readable findings for a pipeline
python -m aicard check demos/01-basic/loan_triage.json --format json

# Generate the Markdown model card
python -m aicard card demos/01-basic/loan_triage.json
```

## What to expect

- The `check` command prints a coverage score and a findings table.
- Because the descriptor omits `manage.monitoring` and leaves
  `measure.fairness` blank, AICARD reports findings. The missing
  post-market monitoring disclosure is a **blocker** (EU AI Act Annex IV 2(g)),
  so the process exits with code **1** - a compliance gate failure.
- Fill in the missing fields and the same command exits **0**.

## Why it matters

NIST AI RMF and the EU AI Act both require structured, auditable disclosures
before a high-risk system is deployed. AICARD turns those requirements into a
linter: zero install, runs in CI, and produces the model card as a build
artifact.
