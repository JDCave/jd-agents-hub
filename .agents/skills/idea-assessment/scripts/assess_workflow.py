#!/usr/bin/env python3
"""Manage the idea-assessment funnel under ``.specify/assessments/<slug>/``.

The utility initializes an assessment directory, copies one stage template at a
time, reports which stage artifacts exist, checks funnel preconditions and the
verdict vocabulary, and prints artifact paths. It never reads or writes source
code and never touches anything outside ``.specify/assessments/``.

Usage:
    python assess_workflow.py [TARGET] [--action ACTION] [--slug SLUG]
        [--root ROOT] [--stage STAGE] [--force] [--json]

Exit codes: 0 = success, 2 = bad input or failed precondition.
"""

import argparse
import json
import re
import sys
from pathlib import Path

STAGE_ORDER = ("intake", "research", "define", "shape", "decide")
STAGE_TEMPLATES = {
    "intake": ("intake.md", "intake-template.md"),
    "research": ("research.md", "research-template.md"),
    "define": ("problem.md", "problem-template.md"),
    "shape": ("concept.md", "concept-template.md"),
    "decide": ("decision.md", "decision-template.md"),
}
VERDICTS = ("go", "needs-clarification", "kill")
ASSESSMENT_PARTS = (".specify", "assessments")
TEMPLATE_DIR_PARTS = ("assets", "report-templates")
VERDICT_LINE = re.compile(
    r"^\s*-\s*\*\*Verdict\*\*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE
)


def normalize_slug(raw):
    """Normalize a user-supplied slug to lowercase kebab-case.

    Raises ValueError for an empty slug or one carrying path separators or
    ``..``; the caller turns that into exit code 2.
    """
    if not isinstance(raw, str):
        raise ValueError("slug must be a string")
    text = raw.strip()
    if not text:
        raise ValueError("empty slug: pass a name made of letters and digits")
    if ".." in text or "/" in text or "\\" in text:
        raise ValueError("unsafe slug: path separators and parent segments are rejected")
    spaced = re.sub(r"[\s_]+", "-", text.lower())
    cleaned = re.sub(r"[^a-z0-9-]", "", spaced)
    collapsed = re.sub(r"-{2,}", "-", cleaned).strip("-")
    if not collapsed:
        raise ValueError(f"slug normalizes to empty: {raw!r}; use letters or digits")
    return collapsed


def stage_artifact(stage):
    """Return the artifact file name produced by one stage."""
    try:
        return STAGE_TEMPLATES[stage][0]
    except KeyError as error:
        raise ValueError(f"unknown stage: {stage}") from error


def stage_template_path(stage):
    """Return the report template path used to seed one stage."""
    try:
        template_name = STAGE_TEMPLATES[stage][1]
    except KeyError as error:
        raise ValueError(f"unknown stage: {stage}") from error
    return Path(__file__).resolve().parent.parent.joinpath(*TEMPLATE_DIR_PARTS, template_name)


def parse_verdict(text):
    """Read the recorded verdict from decision.md content.

    Returns ``(value, invalid)``. An unfilled template line (still carrying the
    ``|`` alternatives) yields ``(None, False)``; an unrecognized word yields
    ``(word, True)``.
    """
    match = VERDICT_LINE.search(text)
    if not match:
        return None, False
    value = match.group(1).strip().strip("`*_ ")
    if "|" in value:
        return None, False
    token = value.lower()
    if token not in VERDICTS:
        return value, True
    return token, False


class AssessmentWorkspace:
    """Resolve and guard the assessment paths for one project root."""

    def __init__(self, root):
        """Store the resolved project root and its assessments directory."""
        self.root = Path(root).expanduser().resolve()
        if not self.root.is_dir():
            raise ValueError(f"project root is not a directory: {self.root}")
        self.base = self.root.joinpath(*ASSESSMENT_PARTS)

    def display(self, path):
        """Render a path relative to the project root, with forward slashes."""
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except (ValueError, OSError):
            return Path(path).as_posix()

    def list_slugs(self):
        """List assessment directory names under the assessments root."""
        if not self.base.is_dir():
            return []
        return sorted(item.name for item in self.base.iterdir() if item.is_dir())

    def assessment_dir(self, slug):
        """Return the guarded assessment directory for a normalized slug."""
        candidate = self.base / slug
        self._guard(candidate)
        return candidate

    def artifact_path(self, slug, stage):
        """Return the guarded artifact path for a stage."""
        return self.assessment_dir(slug) / stage_artifact(stage)

    def _guard(self, candidate):
        """Refuse linked components and paths escaping the assessments root."""
        current = self.root
        for part in candidate.relative_to(self.root).parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f"refusing linked path component: {current}")
        try:
            candidate.resolve().relative_to(self.base.resolve())
        except ValueError as error:
            raise ValueError(
                f"refusing path outside {self.base}: {candidate}"
            ) from error

    def status_one(self, slug):
        """Describe one assessment: stage files present, next stage, verdict."""
        target = self.assessment_dir(slug)
        present = [
            stage_artifact(stage)
            for stage in STAGE_ORDER
            if (target / stage_artifact(stage)).is_file()
        ]
        verdict = None
        if "decision.md" in present:
            try:
                verdict, _invalid = parse_verdict(
                    (target / "decision.md").read_text(encoding="utf-8")
                )
            except OSError as error:
                print(f"warning: cannot read decision.md: {error}", file=sys.stderr)
        missing = [stage for stage in STAGE_ORDER if stage_artifact(stage) not in present]
        return {
            "slug": slug,
            "assessment_dir": self.display(target),
            "stages_present": present,
            "next_stage": missing[0] if missing else None,
            "verdict": verdict,
        }

    def stage_problems(self, slug, stage):
        """List the unmet preconditions for running one stage."""
        target = self.assessment_dir(slug)
        problems = []
        if stage == "shape" and not (target / "problem.md").is_file():
            problems.append(
                "shape requires problem.md; run --action stage --stage define --slug <slug> first"
            )
        if stage == "decide" and not (target / "problem.md").is_file():
            problems.append(
                "decide requires problem.md; run --action stage --stage define --slug <slug> first"
            )
        return problems


def require_slug(args):
    """Return the normalized slug or raise for a missing value."""
    if not args.slug:
        raise ValueError("--slug is required for this action")
    return normalize_slug(args.slug)


def require_stage(args):
    """Return the requested stage, raising when the action needs one."""
    if not args.stage:
        raise ValueError("--stage is required with --action stage")
    return args.stage


def emit(payload, as_json, lines):
    """Print a JSON object or one line per item."""
    if as_json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for line in lines:
            print(line)


def action_init(workspace, args):
    """Create the assessment directory for one slug (idempotent)."""
    slug = require_slug(args)
    target = workspace.assessment_dir(slug)
    created = not target.is_dir()
    target.mkdir(parents=True, exist_ok=True)
    payload = {
        "action": "init",
        "slug": slug,
        "assessment_dir": workspace.display(target),
        "created": created,
    }
    lines = [f"{'created' if created else 'exists'} {payload['assessment_dir']}"]
    emit(payload, args.json, lines)
    return 0


def action_stage(workspace, args):
    """Copy one stage template into the assessment directory."""
    slug = require_slug(args)
    stage = require_stage(args)
    target = workspace.assessment_dir(slug)
    target.mkdir(parents=True, exist_ok=True)
    artifact = workspace.artifact_path(slug, stage)
    if artifact.exists() and not args.force:
        raise ValueError(
            f"{workspace.display(artifact)} already exists; pass --force to overwrite"
        )
    template = stage_template_path(stage)
    content = template.read_text(encoding="utf-8")
    artifact.write_text(content, encoding="utf-8")
    for problem in workspace.stage_problems(slug, stage):
        print(f"warning: {problem}", file=sys.stderr)
    payload = {
        "action": "stage",
        "slug": slug,
        "stage": stage,
        "artifact": artifact.name,
        "path": workspace.display(artifact),
        "created": True,
    }
    lines = [f"staged {payload['path']}"]
    emit(payload, args.json, lines)
    return 0


def action_status(workspace, args):
    """Report stage files present and any recorded verdict."""
    if args.slug:
        slug = require_slug(args)
        payload = {"action": "status", **workspace.status_one(slug)}
        human = _status_lines(payload)
        emit(payload, args.json, human)
        return 0
    entries = [workspace.status_one(slug) for slug in workspace.list_slugs()]
    payload = {"action": "status", "assessments": entries}
    human = []
    for entry in entries:
        human.extend(_status_lines(entry))
    if not entries:
        human = ["no assessments found"]
    emit(payload, args.json, human)
    return 0


def _status_lines(entry):
    """Render one status entry as human-readable lines."""
    stages = ", ".join(entry["stages_present"]) or "none"
    verdict = entry["verdict"] or "none"
    return [
        f"slug: {entry['slug']}",
        f"stages present: {stages}",
        f"next stage: {entry['next_stage'] or 'assessment complete'}",
        f"verdict: {verdict}",
    ]


def action_check(workspace, args):
    """Validate preconditions, verdict vocabulary, and the go downgrade rule."""
    slug = require_slug(args)
    target = workspace.assessment_dir(slug)
    problems = []
    present = []
    if not target.is_dir():
        problems.append(
            "assessment directory not found; run --action init --slug <slug> first"
        )
    else:
        present = [
            stage_artifact(stage)
            for stage in STAGE_ORDER
            if (target / stage_artifact(stage)).is_file()
        ]
        if args.stage:
            problems.extend(workspace.stage_problems(slug, args.stage))
    declared = None
    if "decision.md" in present:
        declared, invalid = parse_verdict(
            (target / "decision.md").read_text(encoding="utf-8")
        )
        if invalid:
            problems.append(
                f"invalid verdict {declared!r}; use go, needs-clarification, or kill"
            )
            declared = None
    effective = declared
    downgraded = declared == "go" and "concept.md" not in present
    if downgraded:
        effective = "needs-clarification"
    missing = [stage for stage in STAGE_ORDER if stage_artifact(stage) not in present]
    payload = {
        "action": "check",
        "slug": slug,
        "stage": args.stage,
        "ok": not problems,
        "stages_present": present,
        "next_stage": missing[0] if missing else None,
        "declared_verdict": declared,
        "verdict": effective,
        "downgraded": downgraded,
        "problems": problems,
    }
    human = [f"slug: {slug}", f"preconditions ok: {payload['ok']}"]
    human.extend(f"problem: {problem}" for problem in problems)
    human.append(f"verdict: {payload['verdict'] or 'none'}")
    emit(payload, args.json, human)
    return 0 if not problems else 2


def action_report(workspace, args):
    """Print the assessment directory or one artifact path."""
    slug = require_slug(args)
    target = workspace.assessment_dir(slug)
    artifact = workspace.artifact_path(slug, args.stage) if args.stage else target
    payload = {
        "action": "report",
        "slug": slug,
        "assessment_dir": workspace.display(target),
        "artifact": args.stage,
        "path": workspace.display(artifact),
        "exists": artifact.exists(),
    }
    lines = [payload["path"], "exists" if payload["exists"] else "missing"]
    emit(payload, args.json, lines)
    return 0


def resolve_root(args):
    """Resolve the project root from --root, the target path, or the cwd."""
    if args.root:
        candidate = Path(args.root).expanduser()
        if not candidate.is_dir():
            raise ValueError(f"--root is not a directory: {candidate}")
        return candidate.resolve()
    if args.target:
        candidate = Path(args.target).expanduser()
        if not candidate.exists():
            raise ValueError(f"target does not exist: {candidate}")
        if candidate.is_file():
            candidate = candidate.parent
        if not candidate.is_dir():
            raise ValueError(f"target is not a directory: {candidate}")
        return candidate.resolve()
    return Path.cwd().resolve()


def build_parser():
    """Build the argparse command line surface."""
    parser = argparse.ArgumentParser(
        prog="assess_workflow",
        description=(
            "Manage .specify/assessments/<slug>/ for the idea-assessment funnel: "
            "init, stage, status, check, and report."
        ),
        epilog=(
            "examples:\n"
            "  assess_workflow.py --action init --slug offline-mode\n"
            "  assess_workflow.py --action stage --stage define --slug offline-mode\n"
            "  assess_workflow.py --action check --slug offline-mode --stage shape\n"
            "  assess_workflow.py --action status --json\n"
            "  assess_workflow.py --help\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target", nargs="?", default=None,
        help="project path or artifact file; a file resolves to its parent directory",
    )
    parser.add_argument(
        "--action", choices=("init", "stage", "status", "check", "report"),
        default="status", help="operation to run (default: status)",
    )
    parser.add_argument("--slug", default=None, help="assessment slug (normalized to [a-z0-9-])")
    parser.add_argument("--root", default=None, help="project root containing .specify/")
    parser.add_argument(
        "--stage", choices=STAGE_ORDER, default=None,
        help="funnel stage: intake, research, define, shape, or decide",
    )
    parser.add_argument(
        "--force", action="store_true", help="overwrite an existing stage artifact",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit one machine-readable JSON object",
    )
    return parser


def main(argv=None):
    """Entry point: dispatch one action and return an exit code."""
    args = build_parser().parse_args(argv)
    handlers = {
        "init": action_init,
        "stage": action_stage,
        "status": action_status,
        "check": action_check,
        "report": action_report,
    }
    try:
        workspace = AssessmentWorkspace(resolve_root(args))
        return handlers[args.action](workspace, args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except FileNotFoundError as error:
        print(f"error: missing file: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: file operation failed: {error}", file=sys.stderr)
        return 2
    except TypeError as error:
        print(f"error: bad argument: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
