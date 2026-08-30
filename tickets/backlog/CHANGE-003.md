---
branch: (none)
created: 2026-08-30
id: CHANGE-003
status: open
tag: (none)
title: Distribute agents and skills to Claude, Codex, OpenCode, and Copilot
type: idea
updated: 2026-08-30
---

## Description

Two-part change:

1. **Multi-tool distribution of agents and skills.** Implement the requirement
   analysis at `tickets/requirement/multi-tool-distribution.md` (committed as part
   of this change). `.agents/` stays the SSOT; a `distribute` command installs
   its agents and skills into Claude Code, Codex, OpenCode, and GitHub Copilot
   (VS Code), using per-target strategies verified against official docs
   (2026-08-30):

   - Skills: Codex and OpenCode scan `.agents/skills/` natively (zero
     distribution); Claude needs `.claude/skills/<name>` symlinks (officially
     supported); Copilot needs `.github/skills/<name>` at project level.
   - Agents: Claude accepts `.agents` layout as-is via `.claude/agents/`
     symlinks (recursive scan, identity from frontmatter `name`); Copilot
     reuses `.claude/agents` or `.github/agents/<name>.md`; OpenCode requires
     generated `<name>.md` (filename = agent name, frontmatter filtered);
     Codex requires generated TOML (`name`, `description`,
     `developer_instructions`).

   Includes exclusion config (agents/skills not installed, global or per
   target), idempotent re-runs, `undistribute` removing exactly what was
   created, drift detection, and portability checks in `validate`. The open
   questions in requirement doc §8 (project vs user scope, exclusion config
   location, OpenCode directory name, kebab-case `name` normalization) are
   resolved with the user at start.

2. **Script rename.** `scripts/init_agents.py` was renamed manually to
   `scripts/init_dotagents_folder.py` (working tree); land it through this
   workflow and update stale references.

## Acceptance criteria

- [ ] `tickets/requirement/multi-tool-distribution.md` committed with this change
- [ ] Rename landed: `scripts/init_agents.py` → `scripts/init_dotagents_folder.py`, references updated
- [ ] `distribute` implements the per-target strategy matrix from requirement doc §3, honoring the exclusion config
- [ ] Generated files (OpenCode `.md`, Codex `.toml`) carry an auto-generated marker and correctly filtered frontmatter
- [ ] Re-running `distribute` is a no-op; `undistribute` removes exactly what was created and reports foreign files it refuses to touch
- [ ] `.agents/` SSOT files are byte-identical after `distribute` / `undistribute` (clean `git status` there)
- [ ] `validate` reports the portability checks (skill `name` matches lowercase-kebab directory name, agent `name` kebab-case, required frontmatter present)
- [ ] Manual verification recorded: after `distribute`, each installed tool discovers the non-excluded agents and skills
- [ ] skill gate PASS (quality ≥90) for all skills and repo-wide audit has no ERROR

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all |  |  |
| python .agents/skills/skill-tester/scripts/audit_skills.py |  |  |

## Progress log

- 2026-08-30 — open: ticket created

## Acceptance record

(Verdict: accepted / rejected · date · notes)

## Release record

- Version: (pending)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
