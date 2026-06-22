# Demo 14 - Auto-insurance premium model (two findings)

**Where the data came from:** an insurer's actuarial governance team preparing
a model file under the NAIC Model Bulletin on AI. The model informs filed-rate
premiums, so unfair-discrimination testing matters.

**What to expect:** this descriptor has **two** distinct findings -

- `measure.fairness` left blank -> **warn** (NIST AI RMF MEASURE 2.11 bias)
- `manage.monitoring` left blank -> **blocker** (EU AI Act Annex IV 2(g))

Because a blocker is present, `check` exits **1**; coverage lands around
**90.6%**. This is the classic "almost there" CI failure.

## Run it

```bash
python -m aicard check demos/14-insurance-pricing/auto_pricing.json
# hand the findings to a GRC spreadsheet
python -m aicard check demos/14-insurance-pricing/auto_pricing.json --format csv > pricing_findings.csv
```

## How to act

The warn (fairness) and the blocker (monitoring) are independent gaps. Document
the disparate-impact testing results in `measure.fairness` and the in-life
loss-ratio / drift monitoring plan in `manage.monitoring`. The CSV export drops
straight into a model-risk tracker for assignment.
