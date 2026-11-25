#!/usr/bin/env python3
"""Unit tests for the bugfix-triage workflow command (read-only, tempdir-based).

The tests never write inside the repository: every workspace lives in a
temporary directory. Sandboxed environments that cannot write the system
temporary directory may point BUGFIX_TRIAGE_TESTDIR at a writable directory.

Run from the skill folder or the repository root:
    python -m unittest discover -s tests
"""

import io
import json
import os
import sys
import tempfile
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import bug_workflow  # noqa: E402

TEST_BASE = os.getenv("BUGFIX_TRIAGE_TESTDIR")
PLACEHOLDERS = {
    "assessment.md": "<valid | likely valid, needs reproduction | invalid>",
    "fix.md": "<applied | partial | not-applied>",
    "test.md": "<verified | partial | failed | not-run>",
}


def record(path, value):
    """Replace a template placeholder in a report file with a recorded value."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(PLACEHOLDERS[path.name], value), encoding="utf-8")


def make_temp_root():
    """Create a unique temporary project root directory.

    Path.mkdir() is used instead of the mode-restricted helper because a
    directory created with owner-only permissions is not usable by every
    sandboxed interpreter. Set BUGFIX_TRIAGE_TESTDIR to choose the parent.
    """
    base = Path(TEST_BASE) if TEST_BASE else Path(tempfile.gettempdir())
    while True:
        candidate = base / f"bugfix-triage-{uuid.uuid4().hex[:12]}"
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue


def remove_workspace(root):
    """Remove a temporary workspace without a recursive bulk delete."""
    try:
        for path in sorted(Path(root).rglob("*"), key=lambda item: len(item.parts), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        Path(root).rmdir()
    except OSError:
        return


class WorkflowTestCase(unittest.TestCase):
    """Give each test its own temporary project root."""

    def setUp(self):
        self.root = make_temp_root()
        self.workspace = bug_workflow.BugWorkspace(self.root)

    def tearDown(self):
        remove_workspace(self.root)

    def init(self, slug="login-timeout", title="Login timeout", force=False):
        """Create one seeded bug workspace and return its payload."""
        return self.workspace.init_bug(slug, title, force)


class SlugTests(WorkflowTestCase):
    """Slug normalization, derivation, and unsafe-input rejection."""

    def test_normalizes_human_text(self):
        self.assertEqual(bug_workflow.normalize_slug("Login Timeout!"), "login-timeout")
        self.assertEqual(bug_workflow.normalize_slug("oauth_redirect 500"), "oauth-redirect-500")
        self.assertEqual(bug_workflow.normalize_slug("--A--B--"), "a-b")

    def test_rejects_empty_and_unsafe_slugs(self):
        for raw in ("", "   ", "***", "../etc", "a/b", "a\\b"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    bug_workflow.normalize_slug(raw)

    def test_derives_bounded_slug_from_title(self):
        slug = bug_workflow.derive_slug("Login times out after a background token refresh in many browsers")
        self.assertLessEqual(len(slug), bug_workflow.MAX_SLUG_LENGTH)
        self.assertTrue(bug_workflow.SAFE_SLUG.match(slug))


class PathSafetyTests(WorkflowTestCase):
    """Target resolution and containment under the bugs directory."""

    def test_file_target_resolves_to_parent(self):
        sample = SKILL_ROOT / "assets" / "sample-bug-report.md"
        self.assertEqual(bug_workflow.resolve_target(str(sample)), sample.parent.resolve())

    def test_missing_target_is_rejected(self):
        with self.assertRaises(ValueError):
            bug_workflow.resolve_target(str(self.root / "no-such-file"))

    def test_bug_directory_stays_under_bugs_root(self):
        directory = self.workspace.slug_directory("login-timeout")
        expected = (self.root / ".specify" / "bugs" / "login-timeout").resolve()
        self.assertEqual(directory, expected)

    def test_escape_slug_is_refused(self):
        with self.assertRaises(ValueError):
            self.workspace.slug_directory("..")

    def test_template_missing_raises_readable_error(self):
        with self.assertRaises(ValueError):
            bug_workflow.read_template("no-such-template.md")


class InitTests(WorkflowTestCase):
    """Workspace creation, template seeding, uniqueness, and overwrite rules."""

    def test_init_creates_directory_and_three_reports(self):
        payload = self.init()
        directory = self.root / ".specify" / "bugs" / "login-timeout"
        self.assertTrue(directory.is_dir())
        for report in bug_workflow.REPORT_FILES:
            self.assertTrue((directory / report).is_file(), report)
        self.assertEqual(payload["created"], list(bug_workflow.REPORT_FILES))
        self.assertFalse(payload["renamed"])

    def test_init_copies_template_content(self):
        self.init()
        seeded = self.root / ".specify" / "bugs" / "login-timeout" / "assessment.md"
        template = SKILL_ROOT / "assets" / "report-templates" / "assessment-template.md"
        self.assertEqual(seeded.read_text(encoding="utf-8"), template.read_text(encoding="utf-8"))

    def test_init_appends_suffixes_for_taken_slugs(self):
        self.assertEqual(self.init()["slug"], "login-timeout")
        self.assertEqual(self.init()["slug"], "login-timeout-2")
        self.assertEqual(self.init()["slug"], "login-timeout-3")

    def test_init_does_not_overwrite_without_force(self):
        self.init()
        seeded = self.root / ".specify" / "bugs" / "login-timeout" / "assessment.md"
        seeded.write_text("hand edited", encoding="utf-8")
        second = self.init()
        self.assertEqual(seeded.read_text(encoding="utf-8"), "hand edited")
        self.assertNotEqual(second["slug"], "login-timeout")

    def test_init_force_rewrites_templates(self):
        self.init()
        seeded = self.root / ".specify" / "bugs" / "login-timeout" / "test.md"
        seeded.write_text("hand edited", encoding="utf-8")
        payload = self.init(force=True)
        self.assertEqual(payload["slug"], "login-timeout")
        self.assertFalse(payload["renamed"])
        self.assertIn("# Bug Verification", seeded.read_text(encoding="utf-8"))

    def test_init_from_title_slug(self):
        payload = self.workspace.init_bug("Login timeout after refresh", "Login timeout after refresh")
        self.assertEqual(payload["slug"], "login-timeout-after-refresh")


class StatusAndCheckTests(WorkflowTestCase):
    """Stage presence, next-stage reporting, and verdict vocabulary rejection."""

    def assessment_path(self):
        return self.root / ".specify" / "bugs" / "login-timeout" / "assessment.md"

    def fix_path(self):
        return self.root / ".specify" / "bugs" / "login-timeout" / "fix.md"

    def test_status_empty_root(self):
        payload = self.workspace.status_bugs()
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["bugs"], [])

    def test_status_lists_seeded_workspace(self):
        self.init()
        payload = self.workspace.status_bugs()
        self.assertEqual(payload["count"], 1)
        bug = payload["bugs"][0]
        self.assertEqual(bug["slug"], "login-timeout")
        self.assertEqual(bug["present"], [])
        self.assertEqual(bug["next_stage"], "assess")
        self.assertTrue(all(bug["files"].values()))

    def test_status_advances_after_recording_a_verdict(self):
        self.init()
        record(self.assessment_path(), "valid")
        bug = self.workspace.status_bugs()["bugs"][0]
        self.assertEqual(bug["present"], ["assess"])
        self.assertEqual(bug["next_stage"], "fix")

    def test_check_reports_next_stage(self):
        self.init()
        payload = self.workspace.check_bug("login-timeout")
        self.assertEqual(payload["next_stage"], "assess")
        self.assertEqual(payload["issues"], [])
        self.assertIsNone(payload["verdicts"]["assessment.md"])

    def test_check_advances_and_keeps_verdict(self):
        self.init()
        record(self.assessment_path(), "likely valid, needs reproduction")
        record(self.fix_path(), "applied")
        payload = self.workspace.check_bug("login-timeout")
        self.assertEqual(payload["next_stage"], "test")
        self.assertEqual(payload["verdicts"]["assessment.md"], "likely valid, needs reproduction")
        self.assertEqual(payload["issues"], [])

    def test_check_rejects_unknown_verdict(self):
        self.init()
        record(self.assessment_path(), "probably a bug")
        payload = self.workspace.check_bug("login-timeout")
        self.assertTrue(payload["issues"])
        self.assertIn("probably a bug", payload["issues"][0])

    def test_check_flags_fix_without_assessment(self):
        self.init()
        record(self.fix_path(), "applied")
        payload = self.workspace.check_bug("login-timeout")
        self.assertTrue(payload["issues"])

    def test_verdict_vocabulary(self):
        self.assertTrue(bug_workflow.verdict_is_known("test.md", "not-run"))
        self.assertTrue(bug_workflow.verdict_is_known("test.md", "Verified."))
        self.assertFalse(bug_workflow.verdict_is_known("test.md", "maybe"))
        self.assertFalse(bug_workflow.verdict_is_known("assessment.md", "applied"))


class ReportAndCliTests(WorkflowTestCase):
    """Artifact paths and the command line surface."""

    def test_report_points_at_next_artifact(self):
        self.init()
        payload = self.workspace.report_bug("login-timeout")
        self.assertEqual(payload["path"], ".specify/bugs/login-timeout/assessment.md")
        self.assertFalse(payload["complete"])

    def test_report_complete_after_three_verdicts(self):
        self.init()
        directory = self.root / ".specify" / "bugs" / "login-timeout"
        record(directory / "assessment.md", "valid")
        record(directory / "fix.md", "applied")
        record(directory / "test.md", "verified")
        payload = self.workspace.report_bug("login-timeout")
        self.assertTrue(payload["complete"])
        self.assertEqual(payload["path"], ".specify/bugs/login-timeout")

    def test_cli_no_args_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(bug_workflow.main([]), 0)

    def test_cli_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as context:
                bug_workflow.main(["--help"])
        self.assertEqual(context.exception.code, 0)

    def test_cli_accepts_sample_file_target(self):
        sample = SKILL_ROOT / "assets" / "sample-bug-report.md"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(bug_workflow.main([str(sample)]), 0)

    def test_cli_init_json_is_parseable(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = bug_workflow.main(
                ["--action", "init", "--slug", "login-timeout", "--root", str(self.root), "--json"]
            )
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["action"], "init")
        self.assertEqual(payload["directory"], ".specify/bugs/login-timeout")

    def test_cli_check_unknown_verdict_exits_two(self):
        self.init()
        record(self.root / ".specify" / "bugs" / "login-timeout" / "assessment.md", "nonsense")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = bug_workflow.main(
                ["--action", "check", "--slug", "login-timeout", "--root", str(self.root)]
            )
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
