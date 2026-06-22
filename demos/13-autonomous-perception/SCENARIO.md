# Demo 13 - ADAS lane & object perception (safety-critical)

**Where the data came from:** an automotive functional-safety team building the
governance file for an SAE Level 2 perception stack (ISO 26262 / ISO 21448
SOTIF / UNECE R157). The descriptor is rich on safety process.

**What to expect:** the team filled in metrics, test data, fairness slices, and
monitoring, but left `measure.limitations` as an **empty list**. Known
limitations are a **blocker** (NIST AI RMF MEASURE 2.6 robustness), so `check`
exits **1**. Coverage score around **93.8%**.

## Run it

```bash
python -m aicard check demos/13-autonomous-perception/lane_perception.json
python -m aicard check demos/13-autonomous-perception/lane_perception.json --format json | jq '.findings'
```

## How to act

Populate `measure.limitations` from the SOTIF edge-case catalogue (e.g.,
"VRU recall degrades below 0.85 in heavy glare", "lane F1 drops on snow-covered
markings", "ODD excludes unmapped construction zones"). These belong in the
card so downstream integrators inherit the operational boundaries.
