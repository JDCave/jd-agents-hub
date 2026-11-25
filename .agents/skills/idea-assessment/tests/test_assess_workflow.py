#!/usr/bin/env python3
"""Unit tests for the idea-assessment workflow utility (read-only, tempdir based)."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import assess_workflow  # noqa: E402


def make_temp_root():
    """Create a fresh temporary project root under the system temp directory."""
    base = Path(tempfile.gettempdir())
    for index in range(200):
        candidate = base / f"idea-assessment-test-{os.getpid()}-{index}"
        if not candidate.exists():
            candidate.mkdir()
            return candidate
    raise RuntimeError("cannot create a temporary project root")


def remove_temp_root(root):
    """Delete a temporary project tree without touching the repository."""
    for path in sorted(Path(root).rglob("*"), key=lambda item: len(item.parts),
                       reverse=True):
        try:
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink()
        except OSError:
            continue
    try:
        Path(root).rmdir()
    except OSError:
        pass


class WorkspaceFixture(unittest.TestCase):
    """Give each test its own temporary project root."""

    def setUp(self):
        """Create a temporary project root."""
        self.root = make_temp_root()

    def tearDown(self):
        """Remove the temporary project root."""
        remove_temp_root(self.root)

    def run_json(self, extra):
        """Run one action against the temp root and parse its JSON output."""
        buffer = io.StringIO()
        argv = list(extra) + ["--root", str(self.root), "--json"]
        with redirect_stdout(buffer):
            code = assess_workflow.main(argv)
        text = buffer.getvalue().strip()
        payload = json.loads(text) if text else {}
        self.assertIsInstance(payload, dict)
        return code, payload

    def assessment_path(self, slug):
        """Return the assessment directory under the temp root."""
        return Path(self.root) / ".specify" / "assessments" / slug

    def write_decision(self, slug, verdict):
        """Record a verdict line in decision.md for a slug."""
        target = self.assessment_path(slug) / "decision.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# Decision\n\n- **Verdict**: {verdict}\n", encoding="utf-8")


class SlugTests(unittest.TestCase):
    """Cover slug normalization and the path-escape refusals."""

    def test_normalizes_case_and_spacing(self):
        self.assertEqual(assess_workflow.normalize_slug("Offline Mode"), "offline-mode")
        self.assertEqual(
            assess_workflow.normalize_slug("cut_onboarding  friction"),
            "cut-onboarding-friction",
        )

    def test_collapses_and_trims_dashes(self):
        self.assertEqual(
            assess_workflow.normalize_slug("--offline---mode--"), "offline-mode"
        )
        self.assertEqual(
            assess_workflow.normalize_slug("  Offline__Mode  "), "offline-mode"
        )

    def test_rejects_empty_slug(self):
        for raw in ("", "   ", "!!!", "___"):
            with self.assertRaises(ValueError):
                assess_workflow.normalize_slug(raw)

    def test_rejects_path_escape_slug(self):
        for raw in ("../evil", "a/b", "a\\b", "..", "a..b", "/etc"):
            with self.assertRaises(ValueError):
                assess_workflow.normalize_slug(raw)

    def test_normalization_is_idempotent(self):
        once = assess_workflow.normalize_slug("Offline Mode!!")
        self.assertEqual(assess_workflow.normalize_slug(once), once)


class InitAndStageTests(WorkspaceFixture):
    """Cover init and stage scaffolding behavior."""

    def test_init_creates_directory(self):
        code, payload = self.run_json(["--action", "init", "--slug", "offline-mode"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["action"], "init")
        self.assertEqual(payload["slug"], "offline-mode")
        self.assertTrue(self.assessment_path("offline-mode").is_dir())
        self.assertEqual(payload["assessment_dir"], ".specify/assessments/offline-mode")

    def test_init_normalizes_slug(self):
        code, payload = self.run_json(["--action", "init", "--slug", "Offline Mode"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["slug"], "offline-mode")
        self.assertTrue(self.assessment_path("offline-mode").is_dir())

    def test_init_rejects_empty_slug(self):
        code, _payload = self.run_json(["--action", "init", "--slug", "!!!"])
        self.assertEqual(code, 2)

    def test_stage_copies_template(self):
        self.run_json(["--action", "init", "--slug", "offline-mode"])
        code, payload = self.run_json(
            ["--action", "stage", "--stage", "define", "--slug", "offline-mode"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["artifact"], "problem.md")
        artifact = self.assessment_path("offline-mode") / "problem.md"
        self.assertTrue(artifact.is_file())
        template = SKILL_ROOT / "assets" / "report-templates" / "problem-template.md"
        self.assertEqual(
            artifact.read_text(encoding="utf-8"),
            template.read_text(encoding="utf-8"),
        )

    def test_stage_refuses_overwrite_without_force(self):
        self.run_json(["--action", "stage", "--stage", "intake", "--slug", "offline-mode"])
        code, _payload = self.run_json(
            ["--action", "stage", "--stage", "intake", "--slug", "offline-mode"]
        )
        self.assertEqual(code, 2)

    def test_stage_force_overwrites(self):
        self.run_json(["--action", "stage", "--stage", "intake", "--slug", "offline-mode"])
        artifact = self.assessment_path("offline-mode") / "intake.md"
        artifact.write_text("edited\n", encoding="utf-8")
        code, _payload = self.run_json(
            ["--action", "stage", "--stage", "intake", "--slug", "offline-mode",
             "--force"]
        )
        self.assertEqual(code, 0)
        self.assertNotEqual(artifact.read_text(encoding="utf-8"), "edited\n")

    def test_unknown_stage_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_workflow.stage_artifact("nope")


class StatusTests(WorkspaceFixture):
    """Cover status reporting."""

    def test_status_lists_stages_present(self):
        self.run_json(["--action", "stage", "--stage", "intake", "--slug", "offline-mode"])
        self.run_json(["--action", "stage", "--stage", "define", "--slug", "offline-mode"])
        code, payload = self.run_json(["--action", "status", "--slug", "offline-mode"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["stages_present"], ["intake.md", "problem.md"])
        self.assertEqual(payload["next_stage"], "research")
        self.assertIsNone(payload["verdict"])

    def test_status_reads_verdict_from_decision(self):
        self.run_json(["--action", "stage", "--stage", "define", "--slug", "offline-mode"])
        self.write_decision("offline-mode", "kill")
        code, payload = self.run_json(["--action", "status", "--slug", "offline-mode"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "kill")

    def test_status_without_slug_lists_assessments(self):
        self.run_json(["--action", "init", "--slug", "one"])
        self.run_json(["--action", "init", "--slug", "two"])
        code, payload = self.run_json(["--action", "status"])
        self.assertEqual(code, 0)
        slugs = [entry["slug"] for entry in payload["assessments"]]
        self.assertEqual(slugs, ["one", "two"])

    def test_status_missing_directory_is_empty(self):
        code, payload = self.run_json(["--action", "status", "--slug", "never-created"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["stages_present"], [])
        self.assertEqual(payload["next_stage"], "intake")


class CheckTests(WorkspaceFixture):
    """Cover funnel preconditions and verdict handling."""

    def test_shape_requires_problem(self):
        self.run_json(["--action", "init", "--slug", "offline-mode"])
        code, payload = self.run_json(
            ["--action", "check", "--slug", "offline-mode", "--stage", "shape"]
        )
        self.assertEqual(code, 2)
        self.assertFalse(payload["ok"])
        self.assertTrue(any("problem.md" in problem for problem in payload["problems"]))

    def test_shape_passes_after_define(self):
        self.run_json(["--action", "stage", "--stage", "define", "--slug", "offline-mode"])
        code, payload = self.run_json(
            ["--action", "check", "--slug", "offline-mode", "--stage", "shape"]
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])

    def test_decide_requires_problem(self):
        self.run_json(["--action", "init", "--slug", "offline-mode"])
        code, payload = self.run_json(
            ["--action", "check", "--slug", "offline-mode", "--stage", "decide"]
        )
        self.assertEqual(code, 2)
        self.assertFalse(payload["ok"])

    def test_go_without_concept_is_downgraded(self):
        self.run_json(["--action", "stage", "--stage", "define", "--slug", "offline-mode"])
        self.write_decision("offline-mode", "go")
        code, payload = self.run_json(
            ["--action", "check", "--slug", "offline-mode", "--stage", "decide"]
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["downgraded"])
        self.assertEqual(payload["declared_verdict"], "go")
        self.assertEqual(payload["verdict"], "needs-clarification")

    def test_go_with_concept_is_kept(self):
        self.run_json(["--action", "stage", "--stage", "define", "--slug", "offline-mode"])
        self.run_json(["--action", "stage", "--stage", "shape", "--slug", "offline-mode"])
        self.write_decision("offline-mode", "go")
        code, payload = self.run_json(["--action", "check", "--slug", "offline-mode"])
        self.assertEqual(code, 0)
        self.assertFalse(payload["downgraded"])
        self.assertEqual(payload["verdict"], "go")

    def test_invalid_verdict_is_rejected(self):
        self.run_json(["--action", "stage", "--stage", "define", "--slug", "offline-mode"])
        self.write_decision("offline-mode", "maybe")
        code, payload = self.run_json(["--action", "check", "--slug", "offline-mode"])
        self.assertEqual(code, 2)
        self.assertTrue(
            any("invalid verdict" in problem for problem in payload["problems"])
        )

    def test_check_missing_assessment_is_rejected(self):
        code, payload = self.run_json(["--action", "check", "--slug", "never-created"])
        self.assertEqual(code, 2)
        self.assertFalse(payload["ok"])


class ReportAndTargetTests(WorkspaceFixture):
    """Cover report paths and file-target resolution."""

    def test_report_prints_artifact_path(self):
        self.run_json(["--action", "stage", "--stage", "intake", "--slug", "offline-mode"])
        code, payload = self.run_json(
            ["--action", "report", "--slug", "offline-mode", "--stage", "intake"]
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["exists"])
        self.assertTrue(payload["path"].endswith("offline-mode/intake.md"))

    def test_report_assessment_directory(self):
        self.run_json(["--action", "init", "--slug", "offline-mode"])
        code, payload = self.run_json(["--action", "report", "--slug", "offline-mode"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["path"], ".specify/assessments/offline-mode")

    def test_file_target_resolves_to_parent(self):
        sample = SKILL_ROOT / "assets" / "sample-idea.md"
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = assess_workflow.main([str(sample), "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["action"], "status")
        self.assertEqual(payload["assessments"], [])

    def test_no_arguments_exits_zero(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = assess_workflow.main([])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
