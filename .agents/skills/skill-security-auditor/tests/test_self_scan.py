"""Smoke tests for skill_security_auditor.py — run with `python -m unittest`."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from skill_security_auditor import (  # noqa: E402
    scan_skill,
    Severity,
)


class AuditorSmokeTest(unittest.TestCase):
    """Scan the auditor's own folder: must PASS with zero critical findings."""

    def test_self_scan_passes(self):
        skill_dir = Path(__file__).resolve().parent.parent
        report = scan_skill(skill_dir)
        criticals = [f for f in report.findings
                     if f.severity == Severity.CRITICAL]
        self.assertEqual(len(criticals), 0,
                         f"unexpected critical findings: {criticals}")

    def test_suppression_directive_is_honored(self):
        skill_dir = Path(__file__).resolve().parent.parent
        report = scan_skill(skill_dir)
        for finding in report.findings:
            self.assertNotIn("detection-patterns.md", finding.file,
                             "noqa-suppressed fixture line was still flagged")


if __name__ == "__main__":
    unittest.main()
