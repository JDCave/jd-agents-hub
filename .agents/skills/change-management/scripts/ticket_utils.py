#!/usr/bin/env python3
"""Deterministic helpers for the change-management ticket workflow.

Subcommands:
  new-ticket    Allocate the next CHANGE id and scaffold tickets/backlog/CHANGE-NNN.md
  next-id       Print the next available CHANGE id without creating anything
  next-version  Print the next semantic version for a ticket type

All commands print human-readable output, or JSON with --json. Exit codes:
0 = success, 2 = runtime error (bad repo, unreadable template, git failure).
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "assets" / "ticket-template.md"
ID_RE = re.compile(r"^CHANGE-(\d+)\.md$")
TICKETS_SUBDIRS = ("backlog", "delivered")


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` until a directory containing .git is found."""
    for candidate in [start, *start.resolve().parents]:
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"no git repository found above {start}")


def existing_ids(tickets_root: Path):
    """Return sorted numeric ids across tickets/backlog/ AND tickets/delivered/.

    Both directories must be scanned so ids are never reused after a ticket
    moves from backlog to delivered.
    """
    ids = []
    for sub in TICKETS_SUBDIRS:
        sub_dir = tickets_root / sub
        if sub_dir.is_dir():
            for entry in sub_dir.iterdir():
                match = ID_RE.match(entry.name)
                if match:
                    ids.append(int(match.group(1)))
    return sorted(ids)


def compute_next_id(tickets_root: Path) -> tuple:
    """Compute the next ticket id as (id, number, existing_ids)."""
    ids = existing_ids(tickets_root)
    number = (ids[-1] + 1) if ids else 1
    return f"CHANGE-{number:03d}", number, ids


def latest_tag_version(repo_root: Path):
    """Return the highest vMAJOR.MINOR.PATCH tag as a tuple, or None."""
    try:
        proc = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=str(repo_root), capture_output=True, text=True, timeout=15,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("git tag --list timed out after 15s")
    except OSError as error:
        raise RuntimeError(f"could not run git: {error}")
    if proc.returncode != 0:
        raise RuntimeError(f"git tag failed: {proc.stderr.strip()}")
    versions = []
    for tag in proc.stdout.split():
        match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag)
        if match:
            versions.append(tuple(int(part) for part in match.groups()))
    return max(versions) if versions else None


def compute_next_version(ticket_type: str, repo_root: Path) -> str:
    """Map ticket type to the next semantic version string."""
    if ticket_type not in ("problem", "idea"):
        raise RuntimeError(f"unknown ticket type: {ticket_type!r} (problem|idea)")
    latest = latest_tag_version(repo_root)
    if latest is None:
        return "v0.1.0"
    major, minor, patch = latest
    if ticket_type == "idea":
        return f"v{major}.{minor + 1}.0"
    return f"v{major}.{minor}.{patch + 1}"


def scaffold_ticket(tickets_root: Path, ticket_id: str, title: str,
                    ticket_type: str) -> Path:
    """Create tickets/backlog/<ticket_id>.md from the template, fields filled in."""
    if not TEMPLATE.is_file():
        raise RuntimeError(f"ticket template not found: {TEMPLATE}")
    if ":" in title:
        raise RuntimeError("title must not contain a colon (header value)")
    backlog_dir = tickets_root / "backlog"
    backlog_dir.mkdir(parents=True, exist_ok=True)
    target = backlog_dir / f"{ticket_id}.md"
    if target.exists():
        raise RuntimeError(f"ticket already exists: {target}")
    try:
        content = TEMPLATE.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError(f"cannot read template {TEMPLATE}: {error}")
    today = datetime.date.today().isoformat()
    replacements = {
        "CHANGE-NNN": ticket_id,
        "title: Short title (no colons)": f"title: {title}",
        "type: problem": f"type: {ticket_type}",
        "YYYY-MM-DD": today,
        "First verifiable criterion": "(to be filled)",
        "Second verifiable criterion": "(to be filled)",
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    try:
        target.write_text(content, encoding="utf-8")
    except OSError as error:
        raise RuntimeError(f"cannot write {target}: {error}")
    return target


def emit(payload: dict, as_json: bool):
    """Print payload as JSON (--json) or key: value lines."""
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ticket_utils",
        description="Deterministic helpers for change tickets "
                    "(see SKILL.md for the full workflow).",
        epilog="examples:\n"
               "  ticket_utils.py new-ticket --type idea --title \"add dark mode\"\n"
               "  ticket_utils.py next-id --json\n"
               "  ticket_utils.py next-version --type problem\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(target, help_text):
        target.add_argument("--json", action="store_true",
                            help="emit machine-readable JSON")
        target.add_argument("--repo", type=Path, default=Path.cwd(),
                            help="path inside the target repo (default: cwd)")
        target.description = help_text

    p_new = sub.add_parser(
        "new-ticket", help="allocate the next id and scaffold a ticket file")
    add_common(p_new, "Scaffold tickets/backlog/CHANGE-NNN.md from the template.")
    p_new.add_argument("--title", required=True,
                       help="short ticket title (no colons)")
    p_new.add_argument("--type", required=True, choices=["problem", "idea"],
                       help="ticket type: problem (fix) or idea (requirement)")

    p_id = sub.add_parser("next-id", help="print the next available CHANGE id")
    add_common(p_id, "Compute the next CHANGE id from existing ticket files.")

    p_ver = sub.add_parser("next-version",
                           help="print the next semantic version for a type")
    add_common(p_ver, "Compute the next semver tag from existing v* tags.")
    p_ver.add_argument("--type", required=True, choices=["problem", "idea"],
                       help="problem bumps patch, idea bumps minor")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        repo_root = find_repo_root(args.repo)
        tickets_dir = repo_root / "tickets"
        if args.command == "next-id":
            ticket_id, number, ids = compute_next_id(tickets_dir)
            emit({"next_id": ticket_id, "next_number": number,
                  "existing": ",".join(str(i) for i in ids) or "(none)"},
                 args.json)
        elif args.command == "next-version":
            version = compute_next_version(args.type, repo_root)
            emit({"type": args.type, "next_version": version}, args.json)
        elif args.command == "new-ticket":
            ticket_id, _, _ = compute_next_id(tickets_dir)
            target = scaffold_ticket(tickets_dir, ticket_id, args.title, args.type)
            emit({"id": ticket_id, "file": str(target),
                  "next": "fill acceptance criteria, then commit"}, args.json)
    except (RuntimeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
