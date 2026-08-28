#!/usr/bin/env python3
"""Initialize and validate a .agents/ directory per the .agents Protocol.

Protocol reference: https://dotagentsprotocol.com/ (see doc/dotagents-protocol.md)

Pure standard library; runs on Windows / macOS / Linux with Python 3.8+.

Usage:
    python scripts/init_agents.py init [--root PATH] [--examples] [--force]
    python scripts/init_agents.py validate [--root PATH]
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

DIRS = ["layouts", "skills", "agents", "tasks", "memories", ".backups"]

AGENTS_MD = """\
# AGENTS.md

Project-wide agent guidelines (AGENTS.md compatible).

<!-- Replace with guidance for coding agents: build commands, code style,
     testing conventions, review rules. -->
"""

MCP_JSON = {"mcpServers": {}}

EXAMPLE_SKILL = """\
---
id: code-review
name: Code Review Expert
description: Thorough code review
enabled: true
---

Review code changes for:
- Security vulnerabilities
- Performance implications
- Test coverage gaps
"""

EXAMPLE_AGENT_MD = """\
---
id: code-reviewer
name: Code Reviewer
description: Reviews code for security
role: delegation-target
enabled: true
connection-type: internal
---

You are a code review specialist.
Focus on security vulnerabilities...
"""

EXAMPLE_AGENT_CONFIG = {
    "toolConfig": {
        "disabledServers": ["filesystem"],
        "enabledBuiltinTools": ["mark_work_complete"],
    },
    "modelConfig": {
        "mcpToolsProviderId": "openai",
        "mcpToolsOpenaiModel": "gpt-4o",
    },
    "connection": {"type": "stdio", "command": "my-agent", "args": ["--mode", "review"]},
}

EXAMPLE_TASK = """\
---
kind: task
id: daily-code-review
name: Daily Code Review
intervalMinutes: 60
enabled: true
runOnStartup: false
---

Review all open pull requests and
summarize their status.
"""

EXAMPLE_MEMORY = """\
---
id: arch_001
title: Database Architecture
content: PostgreSQL with Drizzle ORM
importance: high
tags: database, architecture, orm
---

We chose PostgreSQL over MongoDB for
relational data integrity...
"""

EXAMPLE_FILES = {
    "skills/code-review/SKILL.md": EXAMPLE_SKILL,
    "agents/code-reviewer/agent.md": EXAMPLE_AGENT_MD,
    "agents/code-reviewer/config.json": json.dumps(EXAMPLE_AGENT_CONFIG, indent=2, sort_keys=True) + "\n",
    "tasks/daily-code-review/task.md": EXAMPLE_TASK,
    "memories/arch-decisions.md": EXAMPLE_MEMORY,
}


def atomic_write(path: Path, content: str) -> None:
    """Safe-by-default write: temp file + rename (atomic on POSIX and Windows)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def json_text(obj) -> str:
    # Deterministic key sorting -> clean, minimal git diffs (protocol principle).
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def parse_frontmatter(text: str):
    """Parse simple '---' fenced key:value frontmatter. Returns (dict, body).

    Not full YAML by design; list values stay raw CSV strings.
    Returns (None, text) if no complete frontmatter block is present.
    """
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    meta = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1:])
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return None, text


def cmd_init(root: Path, examples: bool, force: bool) -> int:
    agents_dir = root / ".agents"

    for name in DIRS:
        (agents_dir / name).mkdir(parents=True, exist_ok=True)
        print(f"[dir ] {agents_dir / name}")

    # .gitkeep so empty dirs survive in git
    for name in DIRS:
        keep = agents_dir / name / ".gitkeep"
        if not keep.exists():
            atomic_write(keep, "")
            print(f"[new ] {keep}")

    files = {
        "AGENTS.md": AGENTS_MD,
        "mcp.json": json_text(MCP_JSON),
    }
    if examples:
        files.update(EXAMPLE_FILES)

    for rel, content in sorted(files.items()):
        target = agents_dir / rel
        if target.exists() and not force:
            print(f"[skip] {target} (use --force to overwrite)")
            continue
        existed = target.exists()
        atomic_write(target, content)
        action = "overw" if existed else "new  "
        print(f"[{action}] {target}")

    print(f"\nDone. Next: edit {agents_dir / 'AGENTS.md'} and "
          f"{agents_dir / 'mcp.json'}, then commit .agents/ to git.")
    return 0


def iter_md_files(directory: Path):
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.rglob("*.md") if p.name != ".gitkeep")


def check_md(path: Path, required_keys, errors, warnings):
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    rel = path.relative_to(path.parents[-2] if len(path.parents) >= 2 else path.parent)
    if meta is None:
        errors.append(f"{path}: missing '---' frontmatter block")
        return
    for key in required_keys:
        if key not in meta or not meta[key]:
            errors.append(f"{path}: frontmatter missing required key '{key}'")
    if not body.strip():
        warnings.append(f"{path}: empty body")


def cmd_validate(root: Path) -> int:
    agents_dir = root / ".agents"
    errors, warnings = [], []

    if not agents_dir.is_dir():
        print(f"error: {agents_dir} not found; run 'init' first", file=sys.stderr)
        return 1

    for name in DIRS:
        if not (agents_dir / name).is_dir():
            warnings.append(f"missing directory: {agents_dir / name}")

    # JSON files must parse and be well-formed objects
    json_files = [p for p in agents_dir.rglob("*.json") if ".backups" not in p.parts]
    for path in sorted(json_files):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{path}: invalid JSON ({exc})")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: top-level value must be an object")

    for path in iter_md_files(agents_dir / "skills"):
        check_md(path, ["id", "name", "description"], errors, warnings)

    for path in iter_md_files(agents_dir / "agents"):
        check_md(path, ["id", "name", "description"], errors, warnings)

    for path in iter_md_files(agents_dir / "memories"):
        check_md(path, ["id", "title"], errors, warnings)

    for path in iter_md_files(agents_dir / "tasks"):
        text = path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        if meta is None:
            errors.append(f"{path}: missing '---' frontmatter block")
        else:
            if meta.get("kind") != "task":
                errors.append(f"{path}: frontmatter key 'kind' must be 'task'")
            if not meta.get("id"):
                errors.append(f"{path}: frontmatter missing required key 'id'")
            if not meta.get("intervalMinutes"):
                warnings.append(f"{path}: no 'intervalMinutes' set (one-shot task?)")

    for path in sorted(agents_dir.glob("*.md")):
        pass  # top-level md (agents.md, system-prompt.md) has no required format

    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)

    checked = len(json_files) + sum(
        len(list(iter_md_files(agents_dir / d))) for d in ("skills", "agents", "memories", "tasks")
    )
    if errors:
        print(f"\nFAIL: {len(errors)} error(s), {len(warnings)} warning(s) in {checked} file(s)")
        return 1
    print(f"OK: {checked} file(s) valid, {len(warnings)} warning(s)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create .agents/ structure and starter files")
    p_init.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: cwd)")
    p_init.add_argument("--examples", action="store_true", help="also create example skill/agent/task/memory")
    p_init.add_argument("--force", action="store_true", help="overwrite existing files")

    p_val = sub.add_parser("validate", help="check .agents/ structure and file formats")
    p_val.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: cwd)")

    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to a legacy codepage
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if args.command == "init":
        return cmd_init(args.root, args.examples, args.force)
    return cmd_validate(args.root)


if __name__ == "__main__":
    sys.exit(main())
