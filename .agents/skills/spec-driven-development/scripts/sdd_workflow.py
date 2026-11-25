#!/usr/bin/env python3
"""Manage the .specify workspace for spec-driven development.

Actions:
    bootstrap         Create the .specify skeleton and seed the constitution
    new-feature       Allocate specs/NNN-slug/, write spec.md, persist feature.json
    prereqs           Resolve the current feature paths and available documents
    plan              Copy the plan page template into the current feature
    tasks             Copy the tasks page template into the current feature
    status            Summarize the .specify workspace and the current feature
    resolve-template  Resolve a page template and print its content

Usage:
    python scripts/sdd_workflow.py [TARGET] [--action ACTION] [--json]
    python scripts/sdd_workflow.py . --action bootstrap --json
    python scripts/sdd_workflow.py . --action new-feature --title "add user authentication"
    python scripts/sdd_workflow.py . --action resolve-template --template spec-template

Exit codes: 0 = success, 2 = bad input or a missing prerequisite.
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_ROOT / "assets" / "templates"
TEMPLATE_NAMES = (
    "constitution-template",
    "spec-template",
    "plan-template",
    "tasks-template",
    "checklist-template",
)
SPECIFY_NAME = ".specify"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEQUENTIAL_RE = re.compile(r"^([0-9]{3,})-(.+)$")
TIMESTAMP_RE = re.compile(r"^[0-9]{8}-[0-9]{6}-")
STOP_WORDS = frozenset(
    {
        "a", "an", "and", "as", "at", "build", "create", "feature", "fix", "for",
        "from", "i", "implement", "in", "into", "make", "must", "need", "of", "on",
        "or", "should", "the", "to", "want", "we", "with",
    }
)


class Workspace:
    """Resolved paths for one project workspace that holds a .specify folder."""

    def __init__(self, root):
        self.root = root
        self.specify = root / SPECIFY_NAME
        self.specs = root / "specs"

    def relative(self, path):
        """Return a portable path relative to the workspace root."""
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except ValueError:
            return Path(path).as_posix()

    def pointer_value(self):
        """Read and validate the feature_directory value, or return None."""
        pointer = self.specify / "feature.json"
        if not pointer.is_file():
            return None
        try:
            data = json.loads(pointer.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(data, dict):
            return None
        value = data.get("feature_directory")
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            return validate_relative_path(value, "feature_directory")
        except ValueError:
            return None

    def current_feature(self):
        """Return the current feature directory, or None when no feature exists."""
        pointer = self.pointer_value()
        if pointer is not None:
            candidate = self.root / pointer
            if candidate.is_dir():
                return candidate
        if not self.specs.is_dir():
            return None
        newest = None
        newest_time = -1.0
        for spec_file in self.specs.glob("*/spec.md"):
            try:
                modified = spec_file.stat().st_mtime
            except OSError:
                continue
            if modified > newest_time:
                newest = spec_file.parent
                newest_time = modified
        return newest


def validate_relative_path(raw, label):
    """Validate that a user-supplied path stays inside the workspace root."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{label} is empty")
    path = Path(raw)
    if path.is_absolute() or path.drive:
        raise ValueError(f"{label} must be relative: {raw}")
    if ".." in path.parts:
        raise ValueError(f"{label} must not contain a parent segment: {raw}")
    return path.as_posix()


def normalize_slug(raw):
    """Normalize a user-supplied slug to lowercase kebab-case."""
    if "/" in raw or "\\" in raw or ".." in raw:
        raise ValueError(f"slug must be a plain name without a path segment: {raw}")
    text = re.sub(r"[^a-z0-9]+", "-", raw.strip().lower()).strip("-")
    if not text:
        raise ValueError("slug is empty after normalization")
    if not SLUG_RE.match(text):
        raise ValueError(f"slug is not kebab-case: {raw}")
    if len(text) > 64:
        raise ValueError("slug is longer than 64 characters")
    return text


def derive_slug(title):
    """Derive a 1-4 word kebab slug from a feature title."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    meaningful = [word for word in words if word not in STOP_WORDS and len(word) > 1]
    if not meaningful:
        raise ValueError("cannot derive a slug from the title; pass --slug")
    return normalize_slug("-".join(meaningful[:4]))


def validate_number(value):
    """Validate an explicit feature number."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("number must be a positive integer")
    if not 1 <= value <= 999999:
        raise ValueError("number must be between 1 and 999999")
    return value


def scan_feature_numbers(specs_dir):
    """Return the sequential feature numbers present under specs/."""
    numbers = []
    if not specs_dir.is_dir():
        return numbers
    for entry in specs_dir.iterdir():
        if not entry.is_dir() or TIMESTAMP_RE.match(entry.name):
            continue
        match = SEQUENTIAL_RE.match(entry.name)
        if match:
            numbers.append(int(match.group(1)))
    return sorted(numbers)


def next_feature_number(specs_dir):
    """Return the next sequential feature number under specs/."""
    numbers = scan_feature_numbers(specs_dir)
    if not numbers:
        return 1
    return max(numbers) + 1


def read_text(path):
    """Read a UTF-8 text file, raising a readable error on failure."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValueError(f"missing file: {path}") from error
    except OSError as error:
        raise ValueError(f"unreadable file {path}: {error}") from error


def write_text(path, content):
    """Write a UTF-8 text file, creating parent folders when needed."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def resolve_template(workspace, name):
    """Resolve a page template from the project override, then the bundled asset."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("template name is empty; pass --template NAME")
    clean = name.strip()
    if clean.endswith(".md"):
        clean = clean[:-3]
    if clean not in TEMPLATE_NAMES:
        raise ValueError(
            f"unknown template {name!r}; expected one of: {', '.join(TEMPLATE_NAMES)}"
        )
    project_path = workspace.specify / "templates" / f"{clean}.md"
    if project_path.is_file():
        return clean, "project", read_text(project_path)
    asset_path = TEMPLATE_DIR / f"{clean}.md"
    if not asset_path.is_file():
        raise ValueError(f"bundled template is missing: {asset_path.name}")
    return clean, "skill", read_text(asset_path)


def action_bootstrap(workspace):
    """Create the .specify skeleton and seed the constitution once."""
    workspace.specify.mkdir(parents=True, exist_ok=True)
    created = []
    for name in ("memory", "templates"):
        directory = workspace.specify / name
        if not directory.is_dir():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(f".specify/{name}")
    constitution = workspace.specify / "memory" / "constitution.md"
    if constitution.is_file():
        state = "kept"
    else:
        write_text(constitution, resolve_template(workspace, "constitution-template")[2])
        state = "created"
    payload = {
        "SPECIFY_DIR": SPECIFY_NAME,
        "CREATED_DIRS": created,
        "CONSTITUTION": state,
    }
    lines = [f"SPECIFY_DIR: {SPECIFY_NAME}", f"CONSTITUTION: {state}"]
    lines.extend(f"CREATED: {item}" for item in created)
    return payload, lines


def action_new_feature(workspace, args):
    """Allocate a feature directory, seed spec.md, and persist feature.json."""
    title = (args.title or "").strip()
    slug_arg = (args.slug or "").strip()
    if not title and not slug_arg:
        raise ValueError("provide --title or --slug for new-feature")
    slug = normalize_slug(slug_arg) if slug_arg else derive_slug(title)
    existing = scan_feature_numbers(workspace.specs)
    if args.number is None:
        number = next_feature_number(workspace.specs)
    else:
        number = validate_number(args.number)
        if number in existing:
            bumped = next_feature_number(workspace.specs)
            print(
                f"warning: number {number:03d} is taken; using {bumped:03d} instead",
                file=sys.stderr,
            )
            number = bumped
    feature_dir = workspace.specs / f"{number:03d}-{slug}"
    spec_file = feature_dir / "spec.md"
    if spec_file.is_file() and not args.force:
        raise ValueError(
            f"feature already exists: {workspace.relative(spec_file)} (pass --force to overwrite)"
        )
    write_text(spec_file, resolve_template(workspace, "spec-template")[2])
    pointer = json.dumps(
        {"feature_directory": workspace.relative(feature_dir)}, ensure_ascii=True
    )
    write_text(workspace.specify / "feature.json", pointer + "\n")
    payload = {
        "FEATURE_DIR": workspace.relative(feature_dir),
        "SPEC_FILE": workspace.relative(spec_file),
        "FEATURE_NUM": f"{number:03d}",
    }
    lines = [f"{key}: {value}" for key, value in payload.items()]
    return payload, lines


def action_prereqs(workspace, args):
    """Resolve feature paths and list the design documents that exist."""
    feature_dir = workspace.current_feature()
    if feature_dir is None or not feature_dir.is_dir():
        raise ValueError(
            "feature directory not found; run --action new-feature to create .specify/feature.json"
        )
    paths = {
        "FEATURE_DIR": workspace.relative(feature_dir),
        "FEATURE_SPEC": workspace.relative(feature_dir / "spec.md"),
        "IMPL_PLAN": workspace.relative(feature_dir / "plan.md"),
        "TASKS": workspace.relative(feature_dir / "tasks.md"),
    }
    if args.require_spec and not (feature_dir / "spec.md").is_file():
        raise ValueError(
            f"spec.md is missing in {paths['FEATURE_DIR']}; run --action new-feature"
        )
    if args.require_tasks and not (feature_dir / "tasks.md").is_file():
        raise ValueError(
            f"tasks.md is missing in {paths['FEATURE_DIR']}; run --action tasks"
        )
    documents = []
    for name in ("research.md", "data-model.md", "contracts/", "quickstart.md", "tasks.md"):
        if (feature_dir / name.rstrip("/")).exists():
            documents.append(name)
    payload = dict(paths)
    payload["AVAILABLE_DOCS"] = documents
    lines = [f"{key}: {value}" for key, value in paths.items()]
    lines.append("AVAILABLE_DOCS:")
    lines.extend(f"  {document}" for document in documents)
    return payload, lines


def copy_page_template(workspace, args, template_name, file_name, key):
    """Copy one page template into the current feature without silent overwrite."""
    feature_dir = workspace.current_feature()
    if feature_dir is None or not feature_dir.is_dir():
        raise ValueError(
            "feature directory not found; run --action new-feature before plan or tasks"
        )
    target = feature_dir / file_name
    if target.is_file() and not args.force:
        raise ValueError(
            f"{workspace.relative(target)} already exists (pass --force to overwrite)"
        )
    write_text(target, resolve_template(workspace, template_name)[2])
    payload = {"FEATURE_DIR": workspace.relative(feature_dir), key: workspace.relative(target)}
    lines = [f"{key}: {value}" for key, value in payload.items()]
    return payload, lines


def action_status(workspace):
    """Summarize the .specify workspace and the current feature."""
    feature_dir = workspace.current_feature()
    initialized = workspace.specify.is_dir()
    constitution = (workspace.specify / "memory" / "constitution.md").is_file()
    artifacts = {}
    if feature_dir is not None:
        artifacts = {
            "spec": (feature_dir / "spec.md").is_file(),
            "plan": (feature_dir / "plan.md").is_file(),
            "tasks": (feature_dir / "tasks.md").is_file(),
            "research": (feature_dir / "research.md").is_file(),
            "data_model": (feature_dir / "data-model.md").is_file(),
            "contracts": (feature_dir / "contracts").is_dir(),
            "quickstart": (feature_dir / "quickstart.md").is_file(),
            "checklists": (feature_dir / "checklists").is_dir(),
        }
    found = [name for name, present in artifacts.items() if present]
    feature_label = workspace.relative(feature_dir) if feature_dir is not None else "none"
    summary = (
        f".specify is {'initialized' if initialized else 'not initialized'}; "
        f"current feature: {feature_label}; "
        f"artifacts present: {', '.join(found) if found else 'none'}"
    )
    payload = {
        "specify_initialized": initialized,
        "constitution": constitution,
        "feature_directory": None if feature_dir is None else feature_label,
        "artifacts": artifacts,
        "summary": summary,
    }
    return payload, [summary]


def action_resolve_template(workspace, args):
    """Resolve one page template and return its content."""
    requested = args.template or args.name or ""
    name, source, content = resolve_template(workspace, requested)
    payload = {
        "TEMPLATE_NAME": name,
        "TEMPLATE_SOURCE": source,
        "TEMPLATE_CONTENT": content,
    }
    return payload, [content.rstrip("\n")]


def dispatch(workspace, args):
    """Run the action selected on the command line."""
    if args.action == "bootstrap":
        return action_bootstrap(workspace)
    if args.action == "new-feature":
        return action_new_feature(workspace, args)
    if args.action == "prereqs":
        return action_prereqs(workspace, args)
    if args.action == "plan":
        return copy_page_template(workspace, args, "plan-template", "plan.md", "IMPL_PLAN")
    if args.action == "tasks":
        return copy_page_template(workspace, args, "tasks-template", "tasks.md", "TASKS")
    if args.action == "resolve-template":
        return action_resolve_template(workspace, args)
    return action_status(workspace)


def emit(payload, lines, as_json):
    """Print machine-readable JSON or one line per item."""
    if as_json:
        print(json.dumps(payload, ensure_ascii=True))
        return
    for line in lines:
        print(line)


def resolve_root(raw):
    """Resolve the workspace root; a file argument resolves to its parent folder."""
    candidate = Path(raw).expanduser() if raw else Path.cwd()
    try:
        resolved = candidate.resolve()
    except OSError as error:
        raise ValueError(f"cannot resolve target: {error}") from error
    if not resolved.exists():
        raise ValueError(f"target does not exist: {resolved}")
    if resolved.is_file():
        resolved = resolved.parent
    if not resolved.is_dir():
        raise ValueError(f"target is not a directory: {resolved}")
    return resolved


def target_argument(args):
    """Return the raw target, allowing a lone template name for resolve-template."""
    raw = args.target
    if args.action != "resolve-template" or args.template or args.name:
        return raw
    candidate = (raw or "").strip()
    if candidate and not Path(candidate).exists():
        args.name = candidate
        return None
    return raw


def build_parser():
    """Build the argparse command line surface."""
    parser = argparse.ArgumentParser(
        prog="sdd_workflow",
        description="Manage the .specify workspace for spec-driven development.",
        epilog=(
            "examples:\n"
            "  sdd_workflow.py --action status\n"
            "  sdd_workflow.py . --action bootstrap --json\n"
            "  sdd_workflow.py . --action new-feature --title 'add user authentication'\n"
            "  sdd_workflow.py . --action resolve-template --template spec-template\n"
            "  sdd_workflow.py --help\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="project folder to operate on (default: the current directory); a file resolves to its folder",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default=None,
        help="template name for resolve-template when --template is omitted",
    )
    parser.add_argument(
        "--action",
        choices=[
            "bootstrap",
            "new-feature",
            "prereqs",
            "plan",
            "tasks",
            "status",
            "resolve-template",
        ],
        default="status",
        help="workflow action to run (default: status)",
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON object instead of text")
    parser.add_argument("--title", default=None, help="feature title for new-feature")
    parser.add_argument("--slug", default=None, help="explicit kebab-case slug for new-feature")
    parser.add_argument("--number", type=int, default=None, help="explicit sequential feature number")
    parser.add_argument("--template", default=None, help="page template name for resolve-template")
    parser.add_argument("--force", action="store_true", help="overwrite an existing artifact")
    parser.add_argument("--require-spec", action="store_true", help="fail when spec.md is missing")
    parser.add_argument("--require-tasks", action="store_true", help="fail when tasks.md is missing")
    return parser


def main(argv=None):
    """Run one action and return the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        workspace = Workspace(resolve_root(target_argument(args)))
        payload, lines = dispatch(workspace, args)
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (KeyError, TypeError) as error:
        print(f"error: bad argument: {error}", file=sys.stderr)
        return 2
    emit(payload, lines, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
