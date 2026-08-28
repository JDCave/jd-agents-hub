#!/usr/bin/env python3
"""Guard against plugin skill names that shadow Claude Code built-in commands.

Issue #885: a plugin skill whose frontmatter `name:` equals a built-in slash
command word (e.g. `status`, `review`) shadows the built-in for every user who
installs the plugin — Claude Code's slash resolver matches the bare leaf name.
The fix convention is a namespaced leaf name (`memory-status`, `hub-status`,
`pw-review`, ...). This gate fails CI when a new bare reserved name appears.

Scans every SKILL.md outside mirror trees / docs / eval output and checks the
frontmatter `name:` against the reserved-word list below (Claude Code built-in
commands as of CC 2.1.x — extend the set when new built-ins land).

Exit codes: 0 = clean, 1 = at least one shadowing name found.
"""
import argparse
import json
import os
import re
import sys

# Lives at .agents/skills/skill-builder/scripts/; repo root is 3 levels up
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Claude Code built-in slash commands a plugin skill name must never equal.
RESERVED = {
    "add-dir", "agents", "bug", "clear", "compact", "commit", "config",
    "context", "cost", "doctor", "export", "help", "hooks", "init", "login",
    "logout", "mcp", "memory", "model", "permissions", "plugin", "pr",
    "resume", "review", "rewind", "settings", "status", "terminal", "todos",
    "usage", "vim",
}

SKIP_DIRS = {".git", ".gemini", ".codex", ".vibe", ".hermes", "docs",
             "eval-workspace", "node_modules"}

NAME_RE = re.compile(r'^name:\s*["\']?([A-Za-z0-9_-]+)["\']?\s*$', re.M)


def find_skill_files():
    out = []
    try:
        for root, dirs, files in os.walk(REPO):
            rel = os.path.relpath(root, REPO)
            top = rel.split(os.sep)[0]
            if top in SKIP_DIRS:
                dirs[:] = []
                continue
            if "SKILL.md" in files:
                out.append(os.path.join(root, "SKILL.md"))
    except OSError as e:
        print(f"warning: repo walk interrupted: {e}", file=sys.stderr)
    return sorted(out)


def check(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(2048)
    except FileNotFoundError as e:
        return f"missing: {e}"
    except OSError as e:
        return f"unreadable: {e}"
    m = NAME_RE.search(head)
    if m and m.group(1).lower() in RESERVED:
        return (f"skill name {m.group(1)!r} shadows the built-in "
                f"/{m.group(1).lower()} command (issue #885) — use a "
                f"namespaced leaf name like '<plugin>-{m.group(1).lower()}'")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 epilog="example:\n  %(prog)s --all    # check every SKILL.md, exit 1 on shadowing",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true",
                    help="Check every SKILL.md in the repo (default behavior)")
    ap.add_argument("--json", action="store_true", dest="json_output",
                    help="Emit machine-readable JSON instead of text")
    args = ap.parse_args()

    all_files = find_skill_files()
    failures = {}
    for f in all_files:
        msg = check(f)
        rel = os.path.relpath(f, REPO).replace(os.sep, "/")
        if msg:
            failures[rel] = msg

    if args.json_output:
        print(json.dumps({"files_checked": len(all_files),
                          "failures": failures}, indent=2))
        return 1 if failures else 0

    failed = len(failures)
    for rel, msg in sorted(failures.items()):
        print(f"FAIL {rel}\n  - {msg}")
    if failed:
        print(f"\n{failed} skill(s) shadow built-in commands", file=sys.stderr)
        return 1
    print("OK: no plugin skill name shadows a Claude Code built-in command")
    return 0


if __name__ == "__main__":
    sys.exit(main())
