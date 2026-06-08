"""AICARD — NIST AI RMF / EU AI Act model card generator."""
from __future__ import annotations
import json, time, yaml
from pathlib import Path
from cognis_core import Finding, ScanResult, score

TOOL_NAME = "AICARD"
TOOL_VERSION = "0.1.0"

REQUIRED_FIELDS = [
    ("model_name","critical",3.0),
    ("intended_use","critical",3.0),
    ("training_data_summary","high",2.5),
    ("evaluation_metrics","high",2.5),
    ("risk_assessment","critical",3.0),
    ("human_oversight_plan","high",2.5),
    ("data_governance","high",2.5),
    ("transparency_disclosures","medium",2.0),
    ("post_market_monitoring","medium",2.0),
]

def scan(target: str, **opts) -> ScanResult:
    t0 = time.time()
    result = ScanResult(tool_name=TOOL_NAME, tool_version=TOOL_VERSION, target=str(target))
    p = Path(target)
    manifest = {}
    if p.is_file():
        try:
            if p.suffix in (".yaml",".yml"):
                try:
                    manifest = yaml.safe_load(p.read_text()) or {}
                except Exception:
                    manifest = {}
            else:
                manifest = json.loads(p.read_text())
        except Exception:
            pass
    result.items_scanned = 1
    for field, sev, w in REQUIRED_FIELDS:
        if not manifest.get(field):
            result.add(Finding(
                id=f"AC-EUAI-{field.upper()}", severity=sev, weight=w,
                title=f"MISSING_{field.upper()}",
                description=f"AI Act / NIST RMF required: `{field}` is missing or empty.",
                location=str(target),
                remediation=f"Add `{field}` to the model manifest. See EU AI Act Annex IV.",
                category="ai-act-annex-iv",
                references=["https://artificialintelligenceact.eu/", "https://www.nist.gov/itl/ai-risk-management-framework"],
            ))
    result.composite_score, result.risk_level = score(result.findings)
    result.scan_duration_ms = int((time.time()-t0)*1000)
    return result
