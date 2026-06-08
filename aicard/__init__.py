"""AICARD - Auto-generated NIST AI RMF / EU AI Act Annex IV model & system cards.

Reads a small JSON/INI-free, standard-library description of an AI system and
produces a compliance-oriented model card, scoring it against the disclosure
requirements of:

  * NIST AI Risk Management Framework (AI RMF 1.0) - GOVERN / MAP / MEASURE / MANAGE
  * EU AI Act, Annex IV (technical documentation for high-risk AI systems)

The engine reports *findings* (missing or weak disclosures). A non-empty set of
blocking findings yields a non-zero process exit, so AICARD can gate a CI
pipeline the same way a linter would.
"""

from .core import (
    REQUIREMENTS,
    Finding,
    CardReport,
    load_descriptor,
    evaluate,
    render_card,
    render_report_table,
    report_to_dict,
)

TOOL_NAME = "aicard"
TOOL_VERSION = "1.0.0"

__all__ = [
    "TOOL_NAME",
    "TOOL_VERSION",
    "REQUIREMENTS",
    "Finding",
    "CardReport",
    "load_descriptor",
    "evaluate",
    "render_card",
    "render_report_table",
    "report_to_dict",
]
