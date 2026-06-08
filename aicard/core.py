"""Core engine for AICARD.

No third-party imports. Pure standard library.

A *descriptor* is a JSON document describing an AI system. ``evaluate`` checks
it against a built-in requirement catalogue derived from the NIST AI RMF
functions and EU AI Act Annex IV documentation points, returning a structured
``CardReport``. ``render_card`` turns a (sufficiently complete) descriptor into
a Markdown model card.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


# --------------------------------------------------------------------------- #
# Requirement catalogue
# --------------------------------------------------------------------------- #
# Each requirement maps a dotted descriptor path to a regulatory citation and a
# severity. ``min_len`` enforces that free-text fields are substantive rather
# than a single placeholder word. ``severity`` of "blocker" makes a missing
# field fail the build; "warn" is advisory.

@dataclass(frozen=True)
class Requirement:
    key: str            # dotted path into the descriptor
    title: str          # human label
    framework: str      # NIST AI RMF | EU AI Act Annex IV
    citation: str       # specific function / clause
    severity: str       # "blocker" | "warn"
    min_len: int = 0    # minimum chars for string fields (0 = presence only)
    list_min: int = 0   # minimum items for list fields


REQUIREMENTS: List[Requirement] = [
    # ---- Identity / provenance (Annex IV(1)) ----
    Requirement("system.name", "System name", "EU AI Act Annex IV",
                "1(a) general description", "blocker", min_len=2),
    Requirement("system.version", "Version", "EU AI Act Annex IV",
                "1(a) general description", "blocker", min_len=1),
    Requirement("system.provider", "Provider / responsible party",
                "EU AI Act Annex IV", "1(a) provider", "blocker", min_len=2),
    Requirement("system.intended_purpose", "Intended purpose",
                "EU AI Act Annex IV", "1(b) intended purpose", "blocker",
                min_len=20),
    Requirement("system.deployment_context", "Deployment context",
                "EU AI Act Annex IV", "1(c) hardware/context", "warn",
                min_len=10),

    # ---- NIST GOVERN ----
    Requirement("governance.owner", "Accountable owner", "NIST AI RMF",
                "GOVERN 2.1 roles & responsibilities", "blocker", min_len=2),
    Requirement("governance.policies", "Risk policies referenced",
                "NIST AI RMF", "GOVERN 1.1 legal/policy", "warn", list_min=1),
    Requirement("governance.oversight", "Human oversight measures",
                "EU AI Act Annex IV", "2(e) human oversight", "blocker",
                min_len=15),

    # ---- NIST MAP ----
    Requirement("map.intended_users", "Intended users / affected parties",
                "NIST AI RMF", "MAP 1.1 context", "blocker", list_min=1),
    Requirement("map.out_of_scope", "Out-of-scope / prohibited uses",
                "NIST AI RMF", "MAP 1.1 context", "blocker", list_min=1),
    Requirement("map.risks", "Identified risks", "NIST AI RMF",
                "MAP 5.1 impact characterization", "blocker", list_min=1),

    # ---- NIST MEASURE ----
    Requirement("measure.metrics", "Performance metrics", "NIST AI RMF",
                "MEASURE 2.1 evaluation", "blocker", list_min=1),
    Requirement("measure.test_data", "Test / evaluation data description",
                "EU AI Act Annex IV", "2(d) data & datasets", "blocker",
                min_len=15),
    Requirement("measure.fairness", "Bias / fairness assessment",
                "NIST AI RMF", "MEASURE 2.11 bias", "warn", min_len=15),
    Requirement("measure.limitations", "Known limitations", "NIST AI RMF",
                "MEASURE 2.6 robustness", "blocker", list_min=1),

    # ---- NIST MANAGE ----
    Requirement("manage.mitigations", "Risk mitigations", "NIST AI RMF",
                "MANAGE 1.3 risk treatment", "blocker", list_min=1),
    Requirement("manage.monitoring", "Post-deployment monitoring",
                "EU AI Act Annex IV", "2(g) post-market monitoring",
                "blocker", min_len=15),
    Requirement("manage.incident_contact", "Incident / contact channel",
                "NIST AI RMF", "MANAGE 4.3 incident response", "warn",
                min_len=5),
]


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass
class Finding:
    key: str
    title: str
    framework: str
    citation: str
    severity: str        # "blocker" | "warn"
    detail: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "title": self.title,
            "framework": self.framework,
            "citation": self.citation,
            "severity": self.severity,
            "detail": self.detail,
        }


@dataclass
class CardReport:
    descriptor: Dict[str, Any]
    findings: List[Finding] = field(default_factory=list)
    total_requirements: int = 0

    @property
    def blockers(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == "blocker"]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == "warn"]

    @property
    def satisfied(self) -> int:
        return self.total_requirements - len(self.findings)

    @property
    def score(self) -> float:
        """Coverage score 0-100 weighting blockers double vs warnings."""
        if self.total_requirements == 0:
            return 100.0
        # Each blocker miss costs 2 weight units, each warn miss costs 1.
        max_weight = sum(2 if r.severity == "blocker" else 1
                         for r in REQUIREMENTS)
        lost = sum(2 if f.severity == "blocker" else 1 for f in self.findings)
        return round(100.0 * (max_weight - lost) / max_weight, 1)

    @property
    def compliant(self) -> bool:
        return len(self.blockers) == 0


# --------------------------------------------------------------------------- #
# Loading & evaluation
# --------------------------------------------------------------------------- #

def load_descriptor(path: str) -> Dict[str, Any]:
    """Load a descriptor JSON file. Raises ValueError on malformed input."""
    with open(path, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level descriptor must be a JSON object")
    return data


def _dig(data: Dict[str, Any], dotted: str) -> Any:
    """Return the value at a dotted path, or None if any segment is missing."""
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _check(req: Requirement, value: Any) -> Optional[str]:
    """Return a failure detail string, or None if the requirement is met."""
    if value is None:
        return "field is absent"
    if req.list_min:
        if not isinstance(value, list):
            return "expected a list of entries"
        items = [str(x).strip() for x in value if str(x).strip()]
        if len(items) < req.list_min:
            return f"needs at least {req.list_min} entr" \
                   f"{'y' if req.list_min == 1 else 'ies'}, found {len(items)}"
        return None
    # string-ish field
    text = value if isinstance(value, str) else json.dumps(value)
    text = text.strip()
    if not text:
        return "field is empty"
    if req.min_len and len(text) < req.min_len:
        return f"too brief ({len(text)} chars, need >= {req.min_len}) " \
               "to be a meaningful disclosure"
    return None


def evaluate(descriptor: Dict[str, Any]) -> CardReport:
    """Evaluate a descriptor against the requirement catalogue."""
    report = CardReport(descriptor=descriptor,
                        total_requirements=len(REQUIREMENTS))
    for req in REQUIREMENTS:
        detail = _check(req, _dig(descriptor, req.key))
        if detail is not None:
            report.findings.append(Finding(
                key=req.key,
                title=req.title,
                framework=req.framework,
                citation=req.citation,
                severity=req.severity,
                detail=detail,
            ))
    return report


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def _get(d: Dict[str, Any], path: str, default: str = "_Not provided_") -> str:
    v = _dig(d, path)
    if v is None or (isinstance(v, str) and not v.strip()):
        return default
    if isinstance(v, list):
        items = [str(x).strip() for x in v if str(x).strip()]
        return "\n".join(f"- {x}" for x in items) if items else default
    return str(v).strip()


def render_card(report: CardReport) -> str:
    """Render a Markdown model card from the descriptor + compliance summary."""
    d = report.descriptor
    name = _get(d, "system.name", "Unnamed system")
    version = _get(d, "system.version", "0.0.0")
    status = "COMPLIANT" if report.compliant else "NON-COMPLIANT (blockers present)"

    lines: List[str] = []
    lines.append(f"# AI System Card - {name} (v{version})")
    lines.append("")
    lines.append(f"> Generated by AICARD. Disclosure coverage: "
                 f"**{report.score}%** - {status}")
    lines.append("")
    lines.append("## 1. System overview (Annex IV(1))")
    lines.append(f"- **Provider:** {_get(d, 'system.provider')}")
    lines.append(f"- **Intended purpose:** {_get(d, 'system.intended_purpose')}")
    lines.append(f"- **Deployment context:** {_get(d, 'system.deployment_context')}")
    lines.append("")
    lines.append("## 2. Governance (NIST GOVERN)")
    lines.append(f"- **Accountable owner:** {_get(d, 'governance.owner')}")
    lines.append(f"- **Human oversight:** {_get(d, 'governance.oversight')}")
    lines.append("- **Policies referenced:**")
    lines.append(_indent(_get(d, "governance.policies")))
    lines.append("")
    lines.append("## 3. Context & risks (NIST MAP)")
    lines.append("- **Intended users / affected parties:**")
    lines.append(_indent(_get(d, "map.intended_users")))
    lines.append("- **Out-of-scope / prohibited uses:**")
    lines.append(_indent(_get(d, "map.out_of_scope")))
    lines.append("- **Identified risks:**")
    lines.append(_indent(_get(d, "map.risks")))
    lines.append("")
    lines.append("## 4. Evaluation (NIST MEASURE)")
    lines.append("- **Performance metrics:**")
    lines.append(_indent(_get(d, "measure.metrics")))
    lines.append(f"- **Test data:** {_get(d, 'measure.test_data')}")
    lines.append(f"- **Bias / fairness:** {_get(d, 'measure.fairness')}")
    lines.append("- **Known limitations:**")
    lines.append(_indent(_get(d, "measure.limitations")))
    lines.append("")
    lines.append("## 5. Risk management (NIST MANAGE)")
    lines.append("- **Mitigations:**")
    lines.append(_indent(_get(d, "manage.mitigations")))
    lines.append(f"- **Post-deployment monitoring:** {_get(d, 'manage.monitoring')}")
    lines.append(f"- **Incident contact:** {_get(d, 'manage.incident_contact')}")
    lines.append("")
    lines.append("## 6. Compliance findings")
    if not report.findings:
        lines.append("_No outstanding findings - all catalogued disclosures present._")
    else:
        for f in report.findings:
            tag = "BLOCKER" if f.severity == "blocker" else "warn"
            lines.append(f"- **[{tag}]** {f.title} ({f.framework} "
                         f"{f.citation}): {f.detail}")
    lines.append("")
    return "\n".join(lines)


def _indent(block: str) -> str:
    if not block.startswith("-"):
        return f"  {block}"
    return "\n".join("  " + ln for ln in block.splitlines())


def render_report_table(report: CardReport) -> str:
    """Human-readable compliance summary table."""
    lines: List[str] = []
    name = _get(report.descriptor, "system.name", "Unnamed system")
    lines.append(f"AICARD compliance report - {name}")
    lines.append("=" * 60)
    lines.append(f"Coverage score : {report.score}%")
    lines.append(f"Requirements   : {report.satisfied}/{report.total_requirements} satisfied")
    lines.append(f"Blockers       : {len(report.blockers)}")
    lines.append(f"Warnings       : {len(report.warnings)}")
    lines.append(f"Status         : {'COMPLIANT' if report.compliant else 'NON-COMPLIANT'}")
    lines.append("")
    if not report.findings:
        lines.append("No findings - descriptor satisfies all catalogued disclosures.")
        return "\n".join(lines)
    lines.append(f"{'SEV':<8} {'FRAMEWORK':<20} {'REQUIREMENT':<32} DETAIL")
    lines.append("-" * 100)
    order = {"blocker": 0, "warn": 1}
    for f in sorted(report.findings, key=lambda x: (order[x.severity], x.key)):
        sev = "BLOCK" if f.severity == "blocker" else "WARN"
        lines.append(f"{sev:<8} {f.framework:<20} {f.title:<32} {f.detail}")
    return "\n".join(lines)


def report_to_dict(report: CardReport) -> Dict[str, Any]:
    """Serialise a report for JSON / pipeline consumption."""
    return {
        "system": {
            "name": _dig(report.descriptor, "system.name"),
            "version": _dig(report.descriptor, "system.version"),
        },
        "score": report.score,
        "compliant": report.compliant,
        "total_requirements": report.total_requirements,
        "satisfied": report.satisfied,
        "blocker_count": len(report.blockers),
        "warning_count": len(report.warnings),
        "findings": [f.to_dict() for f in report.findings],
    }
