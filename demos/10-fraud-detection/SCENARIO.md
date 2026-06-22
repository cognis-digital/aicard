# Demo 10 - Real-time payment fraud scorer (fully compliant)

**Where the data came from:** a payments processor's model-governance team
prepared this descriptor for a real-time card-fraud model ahead of a
model-risk-committee sign-off. It documents a mature, well-governed system.

**What to expect:** this descriptor satisfies every catalogued NIST AI RMF /
EU AI Act Annex IV disclosure, so `check` reports a **100% coverage score**,
**0 blockers, 0 warnings**, and exits **0** - a green CI gate.

## Run it

```bash
python -m aicard check demos/10-fraud-detection/transaction_fraud.json
python -m aicard card  demos/10-fraud-detection/transaction_fraud.json > FRAUD_CARD.md
```

## How to act

Use this as the *reference shape* of a complete descriptor: copy its structure
and replace the content for your own finding-producing model. Because it is
fully documented, it is the one to diff a new model against when a field
regresses.
