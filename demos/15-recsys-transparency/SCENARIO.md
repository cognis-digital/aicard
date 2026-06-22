# Demo 15 - Social-feed recommender (compliant, one warning)

**Where the data came from:** a social platform's integrity team documenting a
home-feed ranker for DSA systemic-risk and recommender-transparency obligations.

**What to expect:** all *blocking* disclosures are present, so `check` exits
**0** (compliant) - but `manage.incident_contact` was left blank, which is a
**warning** (NIST AI RMF MANAGE 4.3 incident response). Coverage around
**96.9%**. This shows the difference between a green gate and a perfect score.

## Run it

```bash
python -m aicard check demos/15-recsys-transparency/feed_ranker.json
echo "exit code: $?"   # 0, despite the warning
python -m aicard check demos/15-recsys-transparency/feed_ranker.json --format sarif | jq '.runs[0].results[].level'
```

## How to act

The gate passes, but the warning is real audit debt. Add an incident/contact
channel for systemic-risk escalations. Use `--fail-on`-style gating in CI if
you want warnings to block too (here, the SARIF `warning` level lets you decide
in your code-scanning policy).
