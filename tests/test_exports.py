"""Tests for SARIF 2.1.0 / CSV exports, demo integrity, and version source.

Standard library only, no network.
"""

import csv
import glob
import io
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aicard import TOOL_NAME, TOOL_VERSION
from aicard.core import (
    REQUIREMENTS,
    evaluate,
    load_descriptor,
    report_to_csv,
    report_to_sarif,
)
from aicard.cli import main

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEMOS_DIR = os.path.join(ROOT, "demos")
DEMO = os.path.join(DEMOS_DIR, "01-basic", "loan_triage.json")


def _descriptor_files():
    """Every demo descriptor in the real JSON input format."""
    files = []
    for path in sorted(glob.glob(os.path.join(DEMOS_DIR, "*", "*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue
        # Real descriptors are objects with a "system" block.
        if isinstance(data, dict) and "system" in data:
            files.append(path)
    return files


class TestSarif(unittest.TestCase):
    def setUp(self):
        self.report = evaluate(load_descriptor(DEMO))
        self.sarif = report_to_sarif(self.report, descriptor_path=DEMO)

    def test_sarif_version_and_schema(self):
        self.assertEqual(self.sarif["version"], "2.1.0")
        self.assertIn("sarif-schema-2.1.0", self.sarif["$schema"])

    def test_sarif_serialisable(self):
        json.dumps(self.sarif)  # must not raise

    def test_driver_identity(self):
        driver = self.sarif["runs"][0]["tool"]["driver"]
        self.assertEqual(driver["name"], TOOL_NAME)
        self.assertEqual(driver["version"], TOOL_VERSION)

    def test_one_rule_per_requirement(self):
        rules = self.sarif["runs"][0]["tool"]["driver"]["rules"]
        self.assertEqual(len(rules), len(REQUIREMENTS))
        ids = [r["id"] for r in rules]
        self.assertEqual(len(ids), len(set(ids)), "rule ids must be unique")

    def test_results_match_findings(self):
        results = self.sarif["runs"][0]["results"]
        self.assertEqual(len(results), len(self.report.findings))
        rule_ids = {r["id"] for r in self.sarif["runs"][0]["tool"]["driver"]["rules"]}
        for res in results:
            self.assertIn(res["ruleId"], rule_ids)
            self.assertIn(res["level"], ("error", "warning"))

    def test_blocker_maps_to_error(self):
        levels = {}
        for res in self.sarif["runs"][0]["results"]:
            levels[res["properties"]["descriptorKey"]] = res["level"]
        mon = next(f for f in self.report.findings if f.key == "manage.monitoring")
        self.assertEqual(mon.severity, "blocker")
        self.assertEqual(levels["manage.monitoring"], "error")

    def test_location_points_at_descriptor(self):
        loc = self.sarif["runs"][0]["results"][0]["locations"][0]
        uri = loc["physicalLocation"]["artifactLocation"]["uri"]
        self.assertEqual(uri, DEMO)


class TestCsv(unittest.TestCase):
    def setUp(self):
        self.report = evaluate(load_descriptor(DEMO))
        self.csv_text = report_to_csv(self.report)

    def test_header_and_rows(self):
        rows = list(csv.reader(io.StringIO(self.csv_text)))
        self.assertEqual(rows[0],
                         ["rule_id", "severity", "framework", "citation",
                          "key", "title", "detail"])
        self.assertEqual(len(rows) - 1, len(self.report.findings))

    def test_blockers_sort_first(self):
        rows = list(csv.reader(io.StringIO(self.csv_text)))[1:]
        sevs = [r[1] for r in rows]
        # all blockers must precede any warn
        if "blocker" in sevs and "warn" in sevs:
            self.assertLess(sevs.index("warn"), len(sevs))
            self.assertTrue(all(s == "blocker"
                                for s in sevs[:sevs.index("warn")]))


class TestCliExports(unittest.TestCase):
    def test_cli_sarif_emits_valid_json(self):
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["check", DEMO, "--format", "sarif"])
        self.assertEqual(rc, 1)  # blocker present
        doc = json.loads(buf.getvalue())
        self.assertEqual(doc["version"], "2.1.0")

    def test_cli_csv_emits_header(self):
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["check", DEMO, "--format", "csv"])
        self.assertEqual(rc, 1)
        self.assertTrue(buf.getvalue().startswith("rule_id,severity,"))


class TestDemos(unittest.TestCase):
    def test_demo_descriptors_discovered(self):
        files = _descriptor_files()
        self.assertGreaterEqual(len(files), 8)

    def test_every_demo_loads_and_evaluates(self):
        for path in _descriptor_files():
            with self.subTest(demo=os.path.basename(os.path.dirname(path))):
                desc = load_descriptor(path)
                rep = evaluate(desc)
                # Score must be a sane bounded number for every demo.
                self.assertGreaterEqual(rep.score, 0.0)
                self.assertLessEqual(rep.score, 100.0)
                # Exports must round-trip for every demo.
                json.dumps(report_to_sarif(rep, descriptor_path=path))
                report_to_csv(rep)

    def test_demos_cover_compliant_and_noncompliant(self):
        states = set()
        for path in _descriptor_files():
            rep = evaluate(load_descriptor(path))
            states.add(rep.compliant)
        self.assertIn(True, states, "need at least one compliant demo")
        self.assertIn(False, states, "need at least one non-compliant demo")

    def test_each_demo_has_scenario(self):
        for path in _descriptor_files():
            scenario = os.path.join(os.path.dirname(path), "SCENARIO.md")
            with self.subTest(demo=os.path.basename(os.path.dirname(path))):
                self.assertTrue(os.path.isfile(scenario),
                                f"missing SCENARIO.md next to {path}")


class TestVersionSource(unittest.TestCase):
    def test_version_matches_version_file(self):
        vfile = os.path.join(ROOT, "VERSION")
        if os.path.isfile(vfile):
            with open(vfile, "r", encoding="utf-8") as fh:
                expected = fh.read().strip()
            self.assertEqual(TOOL_VERSION, expected)


if __name__ == "__main__":
    unittest.main()
