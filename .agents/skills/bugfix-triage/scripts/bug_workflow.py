#!/usr/bin/env python3
"""Create and inspect per-bug triage workspaces under .specify/bugs/<slug>/.

The assess, fix, and test stages share one slug handle: one directory containing
assessment.md, fix.md, and test.md. This utility seeds that directory from the
bundled report templates, reports which stages are recorded, checks slug safety
and the verdict vocabulary, and prints the next artifact path.

Usage:
    python bug_workflow.py [TARGET] [--action {init,status,check,report}]
                           [--slug SLUG] [--title TITLE] [--root ROOT]
                           [--force] [--json]

Exit codes: 0 = success, 2 = invalid input or unsafe path.
"""

import argparse
import json
import re
import sys
from pathlib import Path

BUGS_RELATIVE = Path(".specify") / "bugs"
REPORT_FILES = ("assessment.md", "fix.md", "test.md")
STAGES = ("assess", "fix", "test")
STAGE_REPORTS = {"assess": "assessment.md", "fix": "fix.md", "test": "test.md"}
FIELD_NAMES = {"assessment.md": "Verdict", "fix.md": "Status", "test.md": "Result"}
ASSESSMENT_VERDICTS = ("valid", "likely valid, needs reproduction", "invalid")
FIX_STATUSES = ("applied", "partial", "not-applied")
TEST_RESULTS = ("verified", "partial", "failed", "not-run")
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "report-templates"
TEMPLATE_FILES = {
    "assessment.md": "assessment-template.md",
    "fix.md": "fix-template.md",
    "test.md": "test-template.md",
}
MAX_SLUG_LENGTH = 60
SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def resolve_target(raw):
    """Resolve a positional target to a directory; a file resolves to its parent."""
    path = Path(raw).expanduser()
    if not path.exists():
        raise ValueError(f"target does not exist: {raw}")
    if path.is_file():
        return path.resolve().parent
    if path.is_dir():
        return path.resolve()
    raise ValueError(f"target is neither a file nor a directory: {raw}")


def normalize_slug(raw):
    """Normalize a slug to lowercase [a-z0-9-] and reject unsafe input."""
    text = str(raw).strip()
    if not text:
        raise ValueError("slug is empty")
    if ".." in text:
        raise ValueError("slug must not contain '..'")
    if "/" in text or "\\" in text:
        raise ValueError("slug must not contain path separators")
    lowered = text.lower().replace("_", "-").replace(" ", "-")
    cleaned = re.sub(r"[^a-z0-9-]+", "-", lowered)
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-")
    if not cleaned:
        raise ValueError(f"slug has no usable characters: {text}")
    return cleaned


def derive_slug(title):
    """Derive a bounded kebab-case slug from a human-readable bug title."""
    slug = normalize_slug(title)
    if len(slug) > MAX_SLUG_LENGTH:
        slug = slug[:MAX_SLUG_LENGTH].rstrip("-")
    return slug


def extract_field(path, field_name):
    """Read one metadata field such as Verdict from a report file, if set."""
    report = Path(path)
    if not report.is_file():
        return None
    try:
        text = report.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValueError(f"missing report file: {report.name}") from error
    except OSError as error:
        raise ValueError(f"unreadable report {report.name}: {error}") from error
    pattern = rf"^\s*[-*]?\s*\*\*{re.escape(field_name)}\*\*\s*:\s*(.+?)\s*$"
    match = re.search(pattern, text, re.MULTILINE)
    if match is None:
        return None
    value = match.group(1).strip()
    if not value or (value.startswith("<") and value.endswith(">")):
        return None
    return value


def normalize_verdict(raw):
    """Lowercase a recorded verdict value and trim trailing punctuation."""
    return " ".join(str(raw).lower().split()).rstrip(".")


def verdict_is_known(report, value):
    """Return True when a report verdict belongs to its documented vocabulary."""
    normalized = normalize_verdict(value)
    if report == "assessment.md":
        return normalized in ASSESSMENT_VERDICTS
    if report == "fix.md":
        return normalized in FIX_STATUSES
    return normalized in TEST_RESULTS


def read_report_fields(directory):
    """Read the verdict-style metadata field from each stage report, if set."""
    base = Path(directory)
    return {
        report: extract_field(base / report, FIELD_NAMES[report])
        for report in REPORT_FILES
    }


def stage_presence(directory):
    """Return which stages have a recorded verdict in their report file."""
    fields = read_report_fields(directory)
    return {
        stage: fields[STAGE_REPORTS[stage]] is not None
        for stage in STAGES
    }


def next_stage_name(presence):
    """Return the first stage without a recorded verdict, or 'complete'."""
    for stage in STAGES:
        if not presence[stage]:
            return stage
    return "complete"


def read_template(template_name):
    """Read one bundled report template as UTF-8 text."""
    path = TEMPLATE_DIR / template_name
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValueError(f"missing bundled template: path name {template_name}") from error
    except OSError as error:
        raise ValueError(f"unreadable bundled template {template_name}: {error}") from error


def target_slug_name(directory, bugs_dir):
    """Return the bug slug when a directory sits directly under the bugs root."""
    resolved = Path(directory)
    base = Path(bugs_dir)
    if resolved.parent != base:
        return None
    name = resolved.name
    if SAFE_SLUG.match(name):
        return name
    return None


class BugWorkspace:
    """Resolve, seed, and inspect one project's .specify/bugs tree."""

    def __init__(self, root):
        """Store the project root string and derive the bugs directory."""
        self.root = Path(root)
        self.root_string = str(root)
        self.bugs_dir = self.root / BUGS_RELATIVE

    def relative(self, path):
        """Return a POSIX-style path relative to the project root."""
        target = Path(path).resolve()
        try:
            return target.relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return target.as_posix()

    def slug_directory(self, slug):
        """Return the contained bug directory for a slug, rejecting escapes."""
        candidate = self.bugs_dir / slug
        if candidate.is_symlink():
            raise ValueError(f"refusing symbolic link directory: {slug}")
        resolved = candidate.resolve()
        base = self.bugs_dir.resolve()
        root_resolved = self.root.resolve()
        if resolved != base and base not in resolved.parents:
            raise ValueError(f"refusing path outside {BUGS_RELATIVE.as_posix()}: {slug}")
        if root_resolved not in resolved.parents:
            raise ValueError("refusing path outside the project root")
        return resolved

    def unique_slug(self, slug):
        """Append -2, -3, and so on until the bug directory name is free."""
        candidate = slug
        suffix = 2
        while (self.bugs_dir / candidate).exists():
            candidate = f"{slug}-{suffix}"
            suffix += 1
        return candidate

    def list_bugs(self):
        """Return one summary object per bug directory, sorted by slug."""
        if not self.bugs_dir.is_dir():
            return []
        summaries = []
        for entry in sorted(self.bugs_dir.iterdir(), key=lambda item: item.name):
            if not entry.is_dir() or entry.is_symlink():
                continue
            presence = stage_presence(entry)
            present = [stage for stage in STAGES if presence[stage]]
            summaries.append(
                {
                    "slug": entry.name,
                    "directory": self.relative(entry),
                    "files": {
                        stage: (entry / STAGE_REPORTS[stage]).is_file()
                        for stage in STAGES
                    },
                    "stages": presence,
                    "present": present,
                    "next_stage": next_stage_name(presence),
                }
            )
        return summaries

    def target_slug(self, target):
        """Infer a slug when the positional target points at a bug directory."""
        resolved = resolve_target(target)
        return target_slug_name(resolved, self.bugs_dir.resolve())

    def resolve_slug(self, requested, target=None):
        """Resolve the working slug from a flag, the target, or a directory scan."""
        if requested:
            return normalize_slug(requested)
        if target is not None:
            inferred = self.target_slug(target)
            if inferred:
                return inferred
        candidates = [bug["slug"] for bug in self.list_bugs()]
        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            raise ValueError("no bug directories found; run --action init first")
        raise ValueError("slug required; candidates: " + ", ".join(candidates))

    def init_bug(self, requested, title=None, force=False):
        """Create a bug directory and seed the three report templates."""
        requested_slug = normalize_slug(requested)
        slug = requested_slug if force else self.unique_slug(requested_slug)
        directory = self.slug_directory(slug)
        if directory.exists() and not force:
            raise ValueError(f"bug directory already exists: {slug}")
        directory.mkdir(parents=True, exist_ok=True)
        created = []
        skipped = []
        for report in REPORT_FILES:
            destination = directory / report
            if destination.exists() and not force:
                skipped.append(report)
                continue
            content = read_template(TEMPLATE_FILES[report])
            destination.write_text(content, encoding="utf-8")
            created.append(report)
        return {
            "action": "init",
            "root": self.root_string,
            "requested_slug": requested_slug,
            "slug": slug,
            "renamed": slug != requested_slug,
            "title": title,
            "directory": self.relative(directory),
            "artifacts": list(REPORT_FILES),
            "created": created,
            "skipped": skipped,
        }

    def status_bugs(self, target=None):
        """Return stage presence for every bug, optionally filtered by target."""
        only_slug = self.target_slug(target) if target is not None else None
        bugs = [
            bug for bug in self.list_bugs()
            if only_slug is None or bug["slug"] == only_slug
        ]
        return {
            "action": "status",
            "root": self.root_string,
            "bugs_root": BUGS_RELATIVE.as_posix(),
            "count": len(bugs),
            "bugs": bugs,
        }

    def check_bug(self, slug):
        """Validate one bug directory and report its next stage."""
        directory = self.slug_directory(slug)
        if not directory.is_dir():
            raise ValueError(f"bug directory does not exist: {slug}")
        fields = read_report_fields(directory)
        presence = {
            stage: fields[STAGE_REPORTS[stage]] is not None
            for stage in STAGES
        }
        issues = []
        for report in REPORT_FILES:
            value = fields[report]
            if value is not None and not verdict_is_known(report, value):
                field = FIELD_NAMES[report]
                issues.append(f"unknown {field} value '{value}' in {report}")
        if presence["fix"] and not presence["assess"]:
            issues.append("fix.md is recorded without a recorded assessment.md")
        if presence["test"] and not (presence["assess"] and presence["fix"]):
            issues.append("test.md is recorded without assessment.md and fix.md")
        return {
            "action": "check",
            "root": self.root_string,
            "slug": slug,
            "directory": self.relative(directory),
            "stages": presence,
            "verdicts": fields,
            "next_stage": next_stage_name(presence),
            "issues": issues,
        }

    def report_bug(self, slug):
        """Return the next artifact path for one bug workspace."""
        directory = self.slug_directory(slug)
        if not directory.is_dir():
            raise ValueError(f"bug directory does not exist: {slug}")
        presence = stage_presence(directory)
        next_stage = next_stage_name(presence)
        if next_stage == "complete":
            artifact = directory
        else:
            artifact = directory / STAGE_REPORTS[next_stage]
        return {
            "action": "report",
            "root": self.root_string,
            "slug": slug,
            "directory": self.relative(directory),
            "next_stage": next_stage,
            "complete": next_stage == "complete",
            "path": self.relative(artifact),
        }


def emit(payload, as_json):
    """Print one payload as a JSON object or as compact text lines."""
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    action = payload.get("action")
    if action == "init":
        print(f"slug: {payload['slug']}")
        print(f"directory: {payload['directory']}")
        print("created: " + ", ".join(payload["created"]))
        if payload["skipped"]:
            print("skipped: " + ", ".join(payload["skipped"]))
        if payload["renamed"]:
            print(f"note: requested slug {payload['requested_slug']} was taken")
        return
    if action == "status":
        for bug in payload["bugs"]:
            recorded = ", ".join(bug["present"]) if bug["present"] else "no stages recorded"
            print(f"{bug['slug']}: {recorded}; next {bug['next_stage']}")
        if not payload["bugs"]:
            print(f"no bugs under {payload['bugs_root']}")
        return
    if action == "check":
        print(f"slug: {payload['slug']}")
        print(f"directory: {payload['directory']}")
        recorded = [stage for stage in STAGES if payload["stages"][stage]]
        print("stages: " + (", ".join(recorded) if recorded else "none"))
        print(f"next stage: {payload['next_stage']}")
        for issue in payload["issues"]:
            print(f"issue: {issue}", file=sys.stderr)
        return
    print(f"path: {payload['path']}")
    print(f"next stage: {payload['next_stage']}")


def build_parser():
    """Build the argparse command line surface for the workflow."""
    parser = argparse.ArgumentParser(
        prog="bug_workflow",
        description=(
            "Seed and inspect per-bug triage workspaces under .specify/bugs/<slug>/."
        ),
        epilog=(
            "examples:\n"
            '  bug_workflow.py --action init --slug login-timeout --title "Login timeout"\n'
            "  bug_workflow.py --action status --root . --json\n"
            "  bug_workflow.py --action check --slug login-timeout\n"
            "  bug_workflow.py assets/sample-bug-report.md\n"
            "  bug_workflow.py --help\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target", nargs="?", default=None,
        help="optional bug directory or asset path; a file resolves to its parent",
    )
    parser.add_argument(
        "--action", choices=("init", "status", "check", "report"), default="status",
        help="operation to perform (default: status)",
    )
    parser.add_argument(
        "--slug", default=None,
        help="bug slug; normalized to lowercase kebab-case",
    )
    parser.add_argument(
        "--title", default=None,
        help="human-readable bug title whose slug can seed a new workspace",
    )
    parser.add_argument(
        "--root", default=".",
        help="project root that contains .specify/bugs (default: current directory)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="reuse an existing slug directory and overwrite its report templates",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="emit one machine-readable JSON object instead of text lines",
    )
    return parser


def main(argv=None):
    """Run one workflow action, print its report, and return an exit code."""
    args = build_parser().parse_args(argv)
    try:
        workspace = BugWorkspace(args.root)
        if args.action == "init":
            if not args.slug and not args.title:
                raise ValueError("init needs --slug or --title")
            requested = args.slug if args.slug else derive_slug(args.title)
            payload = workspace.init_bug(requested, args.title, args.force)
        elif args.action == "status":
            payload = workspace.status_bugs(args.target)
        elif args.action == "check":
            slug = workspace.resolve_slug(args.slug, args.target)
            payload = workspace.check_bug(slug)
        else:
            slug = workspace.resolve_slug(args.slug, args.target)
            payload = workspace.report_bug(slug)
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (KeyError, TypeError) as error:
        print(f"error: bad input: {error}", file=sys.stderr)
        return 2
    emit(payload, args.json)
    if args.action == "check" and payload.get("issues"):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
