"""Hardening tests for AICARD: error-path and edge-case coverage.

All tests use the standard library only; no network calls.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aicard.core import (
    CardReport,
    Finding,
    evaluate,
    load_descriptor,
    render_report_table,
)
from aicard.cli import main


class TestLoadDescriptorHardening(unittest.TestCase):
    """load_descriptor must return a clean ValueError for every bad-input case."""

    def _tmp_json(self, content: bytes, suffix: str = ".json") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.write(fd, content)
        os.close(fd)
        self.addCleanup(os.unlink, path)
        return path

    def test_binary_file_raises_value_error(self):
        """Non-UTF-8 binary data must raise ValueError, not UnicodeDecodeError."""
        path = self._tmp_json(b"\xff\xfe\x00 binary garbage")
        with self.assertRaises(ValueError) as cm:
            load_descriptor(path)
        self.assertIn("UTF-8", str(cm.exception))

    def test_empty_file_raises_value_error(self):
        """Empty file is invalid JSON and must raise ValueError."""
        path = self._tmp_json(b"")
        with self.assertRaises(ValueError) as cm:
            load_descriptor(path)
        self.assertIn("invalid JSON", str(cm.exception))

    def test_json_list_raises_value_error(self):
        """A JSON array at the top level is not a valid descriptor."""
        path = self._tmp_json(b"[1, 2, 3]")
        with self.assertRaises(ValueError) as cm:
            load_descriptor(path)
        self.assertIn("JSON object", str(cm.exception))

    def test_malformed_json_raises_value_error(self):
        """Truncated / malformed JSON must raise ValueError."""
        path = self._tmp_json(b'{"system": {')
        with self.assertRaises(ValueError) as cm:
            load_descriptor(path)
        self.assertIn("invalid JSON", str(cm.exception))


class TestCliHardening(unittest.TestCase):
    """CLI must return exit code 2 for all user-input errors."""

    def _write_tmp(self, content: bytes, suffix: str = ".json") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.write(fd, content)
        os.close(fd)
        self.addCleanup(os.unlink, path)
        return path

    def test_binary_file_exits_2(self):
        """Binary (non-UTF-8) file must produce exit code 2, not a traceback."""
        path = self._write_tmp(b"\xff\xfe binary")
        rc = main(["check", path])
        self.assertEqual(rc, 2)

    def test_empty_json_file_exits_2(self):
        """Empty file is a user-input error -> exit code 2."""
        path = self._write_tmp(b"")
        rc = main(["check", path])
        self.assertEqual(rc, 2)

    def test_missing_file_card_exits_2(self):
        """Missing file on 'card' subcommand must also return exit 2."""
        rc = main(["card", "no-such-file-xyz.json"])
        self.assertEqual(rc, 2)


class TestRenderReportTableHardening(unittest.TestCase):
    """render_report_table must not KeyError on unexpected severity strings."""

    def test_unknown_severity_does_not_raise(self):
        """A Finding with an unrecognised severity must sort without KeyError."""
        report = CardReport(descriptor={}, total_requirements=2)
        report.findings.append(
            Finding("x.y", "Title", "NIST AI RMF", "X 1.1", "blocker", "absent")
        )
        report.findings.append(
            Finding("x.z", "Other", "EU AI Act", "2(a)", "unrecognised", "detail")
        )
        # Must not raise; unknown severity should sort after known ones
        output = render_report_table(report)
        self.assertIn("BLOCK", output)
        self.assertIn("Other", output)


class TestEvaluateEdgeCases(unittest.TestCase):
    """evaluate() must handle unusual but valid Python inputs gracefully."""

    def test_empty_descriptor_produces_all_findings(self):
        """An empty dict must generate a finding for every requirement."""
        from aicard.core import REQUIREMENTS
        report = evaluate({})
        self.assertEqual(len(report.findings), len(REQUIREMENTS))
        self.assertFalse(report.compliant)

    def test_list_of_empty_strings_counts_as_missing(self):
        """A list containing only whitespace strings must not satisfy list_min."""
        desc = {"map": {"intended_users": ["", "   ", "\t"]}}
        report = evaluate(desc)
        keys = {f.key for f in report.findings}
        self.assertIn("map.intended_users", keys)

    def test_score_zero_when_all_requirements_fail(self):
        """Score must be 0.0 when every requirement has a finding."""
        report = evaluate({})
        self.assertEqual(report.score, 0.0)


if __name__ == "__main__":
    unittest.main()

