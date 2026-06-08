"""Smoke tests for AICARD. Standard library only, no network."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aicard import (
    TOOL_NAME,
    TOOL_VERSION,
    REQUIREMENTS,
    load_descriptor,
    evaluate,
    render_card,
    render_report_table,
    report_to_dict,
)
from aicard.cli import main

DEMO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "demos", "01-basic", "loan_triage.json")
)


class TestAicard(unittest.TestCase):
    def setUp(self):
        self.descriptor = load_descriptor(DEMO)
        self.report = evaluate(self.descriptor)

    def test_metadata(self):
        self.assertEqual(TOOL_NAME, "aicard")
        self.assertTrue(TOOL_VERSION)
        self.assertGreaterEqual(len(REQUIREMENTS), 15)

    def test_demo_loads(self):
        self.assertEqual(self.descriptor["system"]["name"], "LoanTriage Assistant")

    def test_demo_has_findings(self):
        # The demo deliberately omits manage.monitoring (blocker) and
        # leaves measure.fairness blank (warn).
        keys = {f.key for f in self.report.findings}
        self.assertIn("manage.monitoring", keys)
        self.assertIn("measure.fairness", keys)

    def test_demo_blocker_makes_noncompliant(self):
        self.assertFalse(self.report.compliant)
        self.assertGreaterEqual(len(self.report.blockers), 1)

    def test_monitoring_is_blocker_severity(self):
        mon = next(f for f in self.report.findings if f.key == "manage.monitoring")
        self.assertEqual(mon.severity, "blocker")

    def test_short_field_flagged_as_too_brief(self):
        bad = {
            "system": {"name": "X", "version": "1", "provider": "Y",
                       "intended_purpose": "short"}
        }
        rep = evaluate(bad)
        purpose = next(f for f in rep.findings if f.key == "system.intended_purpose")
        self.assertIn("brief", purpose.detail)

    def test_score_is_bounded(self):
        self.assertGreater(self.report.score, 0)
        self.assertLess(self.report.score, 100)

    def test_complete_descriptor_is_compliant(self):
        full = dict(self.descriptor)
        full["measure"] = dict(full["measure"])
        full["measure"]["fairness"] = (
            "Demographic-parity and equal-opportunity gaps measured per cohort; "
            "max gap 2.1%, within policy threshold."
        )
        full["manage"] = dict(full["manage"])
        full["manage"]["monitoring"] = (
            "Daily PSI drift checks plus monthly fairness dashboard with alerting."
        )
        rep = evaluate(full)
        self.assertTrue(rep.compliant, msg=render_report_table(rep))
        self.assertEqual(len(rep.blockers), 0)

    def test_report_to_dict_roundtrips(self):
        d = report_to_dict(self.report)
        json.dumps(d)  # must be serialisable
        self.assertEqual(d["system"]["name"], "LoanTriage Assistant")
        self.assertEqual(d["blocker_count"], len(self.report.blockers))
        self.assertEqual(len(d["findings"]), len(self.report.findings))

    def test_render_card_contains_sections(self):
        card = render_card(self.report)
        self.assertIn("# AI System Card - LoanTriage Assistant", card)
        self.assertIn("NIST MEASURE", card)
        self.assertIn("Compliance findings", card)

    def test_cli_check_table_returns_nonzero(self):
        rc = main(["check", DEMO])
        self.assertEqual(rc, 1)

    def test_cli_check_json_returns_nonzero(self):
        rc = main(["check", DEMO, "--format", "json"])
        self.assertEqual(rc, 1)

    def test_cli_card_runs(self):
        rc = main(["card", DEMO])
        self.assertEqual(rc, 1)  # blocker present

    def test_cli_bad_path_returns_usage_error(self):
        rc = main(["check", "does-not-exist.json"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
