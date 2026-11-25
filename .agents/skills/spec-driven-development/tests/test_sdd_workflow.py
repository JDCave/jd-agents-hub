#!/usr/bin/env python3
"""Read-only unit tests for the spec-driven-development workflow helper.

Run from the repo root:
    python -m unittest discover -s .agents/skills/spec-driven-development/tests

Every test works inside a system temporary directory; nothing is written inside
the repository.
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

import sdd_workflow  # noqa: E402

EXPECTED_DIR = SKILL_ROOT / "expected_outputs"


class TempWorkspaceCase(unittest.TestCase):
    """Give every test an isolated project root in the system temp area."""

    def setUp(self):
        self.root = (
            Path(tempfile.gettempdir()) / f"sdd-tests-{uuid.uuid4().hex}" / "project"
        )
        self.root.mkdir(parents=True)

    def run_main(self, argv):
        """Run main() and return (exit_code, stdout, stderr)."""
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = sdd_workflow.main(argv)
        return code, out.getvalue(), err.getvalue()

    def run_json(self, argv):
        """Run main() with --json and return (exit_code, parsed_object_or_None)."""
        code, out, _err = self.run_main([*argv, "--json"])
        payload = json.loads(out) if out.strip() else None
        return code, payload


class SlugTests(unittest.TestCase):
    """Cover slug derivation, normalization, and path safety."""

    def test_derive_slug_keeps_meaningful_words(self):
        self.assertEqual(
            sdd_workflow.derive_slug("Add user authentication"),
            "add-user-authentication",
        )

    def test_derive_slug_keeps_technical_terms(self):
        self.assertEqual(
            sdd_workflow.derive_slug("Implement OAuth2 API integration"),
            "oauth2-api-integration",
        )

    def test_derive_slug_limits_to_four_words(self):
        slug = sdd_workflow.derive_slug("photo album tile preview grouping layout")
        self.assertEqual(slug.count("-") + 1, 4)

    def test_derive_slug_rejects_useless_title(self):
        with self.assertRaises(ValueError):
            sdd_workflow.derive_slug("the and of")

    def test_normalize_slug_accepts_spaces_and_case(self):
        self.assertEqual(sdd_workflow.normalize_slug("My Feature"), "my-feature")

    def test_normalize_slug_rejects_parent_segment(self):
        for raw in ("../evil", "..", "a/b", "a\\b"):
            with self.assertRaises(ValueError):
                sdd_workflow.normalize_slug(raw)

    def test_normalize_slug_rejects_empty(self):
        with self.assertRaises(ValueError):
            sdd_workflow.normalize_slug("   ")


class NumberingTests(TempWorkspaceCase):
    """Cover sequential feature numbering and collision handling."""

    def make_spec(self, name):
        directory = self.root / "specs" / name
        directory.mkdir(parents=True)
        (directory / "spec.md").write_text("# spec", encoding="utf-8")

    def test_scan_ignores_timestamp_names(self):
        self.make_spec("001-alpha")
        self.make_spec("007-beta")
        self.make_spec("20260101-120000-gamma")
        self.assertEqual(
            sdd_workflow.scan_feature_numbers(self.root / "specs"), [1, 7]
        )

    def test_next_number_after_max(self):
        self.make_spec("001-alpha")
        self.make_spec("007-beta")
        self.assertEqual(sdd_workflow.next_feature_number(self.root / "specs"), 8)

    def test_next_number_on_empty_specs(self):
        self.assertEqual(sdd_workflow.next_feature_number(self.root / "specs"), 1)

    def test_explicit_number_collision_bumps_with_warning(self):
        self.make_spec("001-alpha")
        code, payload = self.run_json(
            [str(self.root), "--action", "new-feature", "--title", "add login",
             "--number", "1"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["FEATURE_NUM"], "002")

    def test_feature_number_rolls_over_past_999(self):
        self.make_spec("999-last")
        code, payload = self.run_json(
            [str(self.root), "--action", "new-feature", "--title", "add login"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["FEATURE_NUM"], "1000")


class NewFeatureTests(TempWorkspaceCase):
    """Cover feature allocation, spec seeding, and pointer persistence."""

    def test_new_feature_writes_spec_and_pointer(self):
        code, payload = self.run_json(
            [str(self.root), "--action", "new-feature", "--title", "Add user authentication"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["FEATURE_DIR"], "specs/001-add-user-authentication")
        self.assertEqual(
            payload["SPEC_FILE"], "specs/001-add-user-authentication/spec.md"
        )
        spec = self.root / payload["SPEC_FILE"]
        self.assertTrue(spec.is_file())
        self.assertIn("# Feature Specification", spec.read_text(encoding="utf-8"))
        pointer = json.loads(
            (self.root / ".specify" / "feature.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            pointer["feature_directory"], "specs/001-add-user-authentication"
        )

    def test_new_feature_accepts_explicit_slug(self):
        code, payload = self.run_json(
            [str(self.root), "--action", "new-feature", "--title", "ignored",
             "--slug", "custom-slug"]
        )
        self.assertEqual(code, 0)
        self.assertTrue(payload["FEATURE_DIR"].endswith("-custom-slug"))

    def test_new_feature_rejects_path_escape(self):
        code, _out, err = self.run_main(
            [str(self.root), "--action", "new-feature", "--title", "x",
             "--slug", "../escape"]
        )
        self.assertEqual(code, 2)
        self.assertIn("path segment", err)

    def test_new_feature_without_title_or_slug_fails(self):
        code, _payload = self.run_json([str(self.root), "--action", "new-feature"])
        self.assertEqual(code, 2)

    def test_new_feature_allocates_a_new_number_for_the_same_title(self):
        argv = [str(self.root), "--action", "new-feature", "--title", "add login"]
        self.assertEqual(self.run_main(argv)[0], 0)
        code, payload = self.run_json(argv)
        self.assertEqual(code, 0)
        self.assertEqual(payload["FEATURE_NUM"], "002")
        self.assertEqual(self.run_main([*argv, "--force"])[0], 0)


class PrereqTests(TempWorkspaceCase):
    """Cover prerequisite resolution, gating, and fallback behavior."""

    def test_prereqs_without_feature_fails(self):
        code, _out, err = self.run_main(
            [str(self.root), "--action", "prereqs", "--json"]
        )
        self.assertEqual(code, 2)
        self.assertIn("feature directory not found", err)

    def test_prereqs_requires_tasks_when_asked(self):
        argv = [str(self.root), "--action", "new-feature", "--title", "add login"]
        self.assertEqual(self.run_main(argv)[0], 0)
        code, _out, err = self.run_main(
            [str(self.root), "--action", "prereqs", "--require-tasks"]
        )
        self.assertEqual(code, 2)
        self.assertIn("tasks.md is missing", err)

    def test_prereqs_requires_spec_when_asked(self):
        argv = [str(self.root), "--action", "new-feature", "--title", "add login"]
        self.assertEqual(self.run_main(argv)[0], 0)
        spec = next((self.root / "specs").glob("*/spec.md"))
        spec.unlink()
        code, _payload = self.run_json(
            [str(self.root), "--action", "prereqs", "--require-spec"]
        )
        self.assertEqual(code, 2)

    def test_prereqs_falls_back_to_newest_spec(self):
        specs = self.root / "specs"
        older = specs / "001-older"
        newer = specs / "002-newer"
        older.mkdir(parents=True)
        newer.mkdir(parents=True)
        old_spec = older / "spec.md"
        new_spec = newer / "spec.md"
        old_spec.write_text("# old", encoding="utf-8")
        new_spec.write_text("# new", encoding="utf-8")
        os.utime(old_spec, (1_000, 1_000))
        os.utime(new_spec, (2_000, 2_000))
        code, payload = self.run_json([str(self.root), "--action", "prereqs"])
        self.assertEqual(code, 0)
        self.assertEqual(payload["FEATURE_DIR"], "specs/002-newer")
        os.utime(old_spec, (3_000, 3_000))
        code, payload = self.run_json([str(self.root), "--action", "prereqs"])
        self.assertEqual(payload["FEATURE_DIR"], "specs/001-older")


class PlanTasksTests(TempWorkspaceCase):
    """Cover plan and tasks seeding plus overwrite refusal."""

    def setUp(self):
        super().setUp()
        self.assertEqual(
            self.run_main(
                [str(self.root), "--action", "new-feature", "--title", "add login"]
            )[0],
            0,
        )

    def test_plan_copies_template(self):
        code, payload = self.run_json([str(self.root), "--action", "plan"])
        self.assertEqual(code, 0)
        plan = self.root / payload["IMPL_PLAN"]
        self.assertIn("# Implementation Plan", plan.read_text(encoding="utf-8"))
        self.assertEqual(self.run_main([str(self.root), "--action", "plan"])[0], 2)
        self.assertEqual(
            self.run_main([str(self.root), "--action", "plan", "--force"])[0], 0
        )

    def test_tasks_copies_template(self):
        code, payload = self.run_json([str(self.root), "--action", "tasks"])
        self.assertEqual(code, 0)
        tasks = self.root / payload["TASKS"]
        self.assertIn("# Tasks:", tasks.read_text(encoding="utf-8"))
        self.assertEqual(self.run_main([str(self.root), "--action", "tasks"])[0], 2)
        self.assertEqual(
            self.run_main([str(self.root), "--action", "tasks", "--force"])[0], 0
        )


class TemplateResolutionTests(TempWorkspaceCase):
    """Cover project-override precedence and unknown template handling."""

    def test_falls_back_to_bundled_asset(self):
        code, payload = self.run_json(
            [str(self.root), "--action", "resolve-template", "--template", "spec-template"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["TEMPLATE_SOURCE"], "skill")
        self.assertIn("Feature Specification", payload["TEMPLATE_CONTENT"])

    def test_project_override_wins(self):
        override = self.root / ".specify" / "templates" / "spec-template.md"
        override.parent.mkdir(parents=True)
        override.write_text("# Custom template", encoding="utf-8")
        code, payload = self.run_json(
            [str(self.root), "--action", "resolve-template", "--template", "spec-template"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(payload["TEMPLATE_SOURCE"], "project")
        self.assertEqual(payload["TEMPLATE_CONTENT"], "# Custom template")

    def test_template_name_with_suffix_is_accepted(self):
        code, _payload = self.run_json(
            [str(self.root), "--action", "resolve-template", "--template", "plan-template.md"]
        )
        self.assertEqual(code, 0)

    def test_unknown_template_fails(self):
        for name in ("missing-template", "../spec-template", ""):
            code, _out, err = self.run_main(
                [str(self.root), "--action", "resolve-template", "--template", name]
            )
            self.assertEqual(code, 2)
            self.assertIn("error:", err)


class BootstrapStatusTests(TempWorkspaceCase):
    """Cover bootstrap idempotency and the always-zero status summary."""

    def test_bootstrap_seeds_constitution_once(self):
        code, first = self.run_json([str(self.root), "--action", "bootstrap"])
        self.assertEqual(code, 0)
        self.assertEqual(first["CONSTITUTION"], "created")
        self.assertTrue(
            (self.root / ".specify" / "memory" / "constitution.md").is_file()
        )
        self.assertTrue((self.root / ".specify" / "templates").is_dir())
        code, second = self.run_json([str(self.root), "--action", "bootstrap"])
        self.assertEqual(code, 0)
        self.assertEqual(second["CONSTITUTION"], "kept")

    def test_status_is_always_zero(self):
        code, payload = self.run_json([str(self.root), "--action", "status"])
        self.assertEqual(code, 0)
        self.assertFalse(payload["specify_initialized"])
        self.assertIsNone(payload["feature_directory"])
        self.assertIn("summary", payload)


class SampleToleranceTests(unittest.TestCase):
    """Every sample asset must be accepted as the positional argument."""

    def test_asset_samples_exit_zero(self):
        samples = sorted((SKILL_ROOT / "assets").glob("*sample*"))
        self.assertGreaterEqual(len(samples), 5)
        for sample in samples:
            out = io.StringIO()
            err = io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = sdd_workflow.main([str(sample)])
            self.assertEqual(code, 0, f"{sample.name}: {err.getvalue()}")

    def test_help_exits_zero(self):
        out = io.StringIO()
        with redirect_stdout(out):
            with self.assertRaises(SystemExit) as context:
                sdd_workflow.build_parser().parse_args(["--help"])
        self.assertEqual(context.exception.code, 0)
        self.assertGreater(len(out.getvalue()), 50)


class ExpectedOutputTests(TempWorkspaceCase):
    """The documented expected outputs must match real runs."""

    def test_expected_outputs_are_reproducible(self):
        bootstrap_expected = json.loads(
            (EXPECTED_DIR / "bootstrap.json").read_text(encoding="utf-8")
        )
        feature_expected = json.loads(
            (EXPECTED_DIR / "new-feature.json").read_text(encoding="utf-8")
        )
        prereqs_expected = json.loads(
            (EXPECTED_DIR / "prereqs.json").read_text(encoding="utf-8")
        )
        status_expected = json.loads(
            (EXPECTED_DIR / "status.json").read_text(encoding="utf-8")
        )

        code, bootstrap = self.run_json([str(self.root), "--action", "bootstrap"])
        self.assertEqual(code, 0)
        self.assertEqual(bootstrap, bootstrap_expected)

        code, feature = self.run_json(
            [str(self.root), "--action", "new-feature",
             "--title", "Add user authentication"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(feature, feature_expected)

        self.assertEqual(self.run_main([str(self.root), "--action", "plan"])[0], 0)
        self.assertEqual(self.run_main([str(self.root), "--action", "tasks"])[0], 0)

        code, prereqs = self.run_json(
            [str(self.root), "--action", "prereqs", "--require-spec", "--require-tasks"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(prereqs, prereqs_expected)

        code, status = self.run_json([str(self.root), "--action", "status"])
        self.assertEqual(code, 0)
        self.assertEqual(status, status_expected)


if __name__ == "__main__":
    unittest.main()
