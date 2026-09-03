#!/usr/bin/env python3
"""Initialize and validate a .agents/ directory per the .agents Protocol.

Protocol reference: https://dotagentsprotocol.com/ (see dotagents-protocol.md in this directory)

Pure standard library; runs on Windows / macOS / Linux with Python 3.8+.

Usage:
    python docs/dotagents/init_dotagents_folder.py init [--root PATH] [--examples] [--force]
    python docs/dotagents/init_dotagents_folder.py validate [--root PATH]

This script only creates and checks the folder. Distributing agents/skills into
each AI tool's discovery locations is a separate concern — see distribute.py.
"""

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

DIRS = ["layouts", "skills", "agents", "tasks", "memories", ".backups"]

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

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

    Not full YAML by design; list values stay raw CSV strings. Matching
    surrounding quotes on a value are stripped so `name: "x"` == `name: x`.
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
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            meta[key.strip()] = value
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


def list_ssot(root: Path, kind: str):
    """Names of SSOT entries: agents/<name>/agent.md or skills/<name>/SKILL.md."""
    directory = root / ".agents" / kind
    entry_file = "agent.md" if kind == "agents" else "SKILL.md"
    if not directory.is_dir():
        return []
    return sorted(c.name for c in directory.iterdir()
                  if c.is_dir() and (c / entry_file).is_file())


# --- validate -------------------------------------------------------------------

def iter_md_files(directory: Path):
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.rglob("*.md") if p.name != ".gitkeep")


def check_md(path: Path, required_keys, errors, warnings):
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    if meta is None:
        errors.append(f"{path}: missing '---' frontmatter block")
        return None
    for key in required_keys:
        if key not in meta or not meta[key]:
            errors.append(f"{path}: frontmatter missing required key '{key}'")
    if not body.strip():
        warnings.append(f"{path}: empty body")
    return meta


def cmd_validate(root: Path) -> int:
    agents_dir = root / ".agents"
    errors, warnings = [], []

    if not agents_dir.is_dir():
        print(f"error: {agents_dir} not found; run 'init' first", file=sys.stderr)
        return 1

    for name in DIRS:
        if not (agents_dir / name).is_dir():
            warnings.append(f"missing directory: {agents_dir / name}")

    # JSON files must parse and be well-formed objects (empty placeholders only warn)
    json_files = [p for p in agents_dir.rglob("*.json") if ".backups" not in p.parts]
    for path in sorted(json_files):
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            warnings.append(f"{path}: empty placeholder JSON file")
            continue
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"{path}: invalid JSON ({exc})")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: top-level value must be an object")

    # Skills: one canonical SKILL.md per directory; portability per the Agent Skills standard
    # (name + description required; `id` is protocol-specific and optional here)
    for name in list_ssot(root, "skills"):
        path = agents_dir / "skills" / name / "SKILL.md"
        meta = check_md(path, ["name", "description"], errors, warnings)
        if meta is None:
            continue
        skill_name = meta.get("name", "")
        if skill_name != name:
            errors.append(f"{path}: frontmatter 'name' ({skill_name!r}) must match "
                          f"the directory name ({name!r})")
        elif not KEBAB_RE.match(skill_name) or not 1 <= len(skill_name) <= 64:
            errors.append(f"{path}: name must be 1-64 chars of lowercase kebab-case")
        if len(meta.get("description", "")) > 1024:
            warnings.append(f"{path}: description exceeds 1024 chars "
                            f"(tools may reject or truncate it)")

    # Agents: one canonical agent.md per directory; frontmatter usable by every adapter
    for name in list_ssot(root, "agents"):
        path = agents_dir / "agents" / name / "agent.md"
        meta = check_md(path, ["id", "name", "description"], errors, warnings)
        if meta is None:
            continue
        agent_name = meta.get("name", "")
        if agent_name.startswith("-") or ":" in agent_name:
            errors.append(f"{path}: name must not start with '-' or contain ':' "
                          f"(Claude Code skips such agents)")
        elif not KEBAB_RE.match(agent_name):
            warnings.append(f"{path}: name {agent_name!r} is not lowercase kebab-case — "
                            f"works, but kebab-case matching the id is the portable form")

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

    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)

    checked = (len(json_files) + len(list_ssot(root, "skills")) + len(list_ssot(root, "agents"))
               + sum(len(list(iter_md_files(agents_dir / d))) for d in ("memories", "tasks")))
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

    p_val = sub.add_parser("validate", help="check .agents/ structure, formats, and cross-tool portability")
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
