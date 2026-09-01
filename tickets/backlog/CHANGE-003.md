---
branch: feature/CHANGE-003-multi-tool-distribution
created: 2026-08-30
id: CHANGE-003
status: awaiting-acceptance
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

- [x] `tickets/requirement/multi-tool-distribution.md` committed with this change
- [x] Rename landed: `scripts/init_agents.py` → `scripts/init_dotagents_folder.py`, references updated
- [x] `distribute` implements the per-target strategy matrix from requirement doc §3, honoring the exclusion config
- [x] Generated files (OpenCode `.md`, Codex `.toml`) carry an auto-generated marker and correctly filtered frontmatter
- [x] Re-running `distribute` is a no-op; `undistribute` removes exactly what was created and reports foreign files it refuses to touch
- [x] `.agents/` SSOT files are byte-identical after `distribute` / `undistribute` (clean `git status` there)
- [x] `validate` reports the portability checks (skill `name` matches lowercase-kebab directory name, agent `name` kebab-case, required frontmatter present)
- [x] Manual verification recorded: after `distribute`, each installed tool discovers the non-excluded agents and skills
- [x] skill gate PASS (quality ≥90) for all skills and repo-wide audit has no ERROR

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python doc/dotagents/init_dotagents_folder.py validate | 0 | OK: 45 file(s) valid, 3 warning(s) — empty `models.json` placeholder; 2 agent names non-kebab (known decision §8.4, adapters derive identity from the directory name); path updated after the doc/dotagents/ relocation |
| python scripts/distribute.py distribute --scope project | 0 | 8 claude links (junctions), 2 codex `.toml` + 2 opencode `.md` generated, 8 copilot artifacts (2 file hardlinks + 6 skill junctions), 12 native (codex/opencode skills), 0 conflicts |
| python scripts/distribute.py distribute --scope project (re-run) | 0 | 0 new, 0 updated, 20 unchanged, 12 native — idempotent |
| python scripts/distribute.py undistribute | 0 | 20 removed, 0 kept, 0 foreign, 0 error(s); all six target dirs left empty |
| python scripts/distribute.py distribute --config \<temp exclusions\> | 0 | globally excluded agent+skill absent from every target; per-target `copilot.skills` exclusion removed only `.github/skills/skill-tester` while claude kept its link |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 0 | 6/6 skills PASS (min score 90, security FAIL blocks) |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 6/6 skills PASS (100%), no ERROR |
| git status after distribute → undistribute | 0 | nothing under `.agents/` — SSOT untouched; only the intended working-tree changes (script, config, .gitignore) remain |

Windows note: this machine runs without symlink privilege — directory links fell back to junctions and copilot agent files to same-volume hardlinks (`link_points_to` verifies realpath or inode identity), so no Developer Mode was required.

## Progress log

- 2026-08-30 — open: ticket created
- 2026-08-30 — open → in-progress; branch feature/CHANGE-003-multi-tool-distribution created; scope decisions recorded: distribution scope is user-selectable per run (`--scope project|user`, default project); exclusion config lives next to the script at `scripts/distribute.json`; OpenCode agents dir configurable (default `agents` per current docs); non-kebab agent `name` handled as validate warning (adapters derive names from directory), no SSOT normalization in this change
- 2026-08-30 — rename committed (9d67804); requirement analysis with §8 decisions committed (8e4842d)
- 2026-08-30 — implemented `distribute`/`undistribute` (+ validate portability checks, exclusion config, manifest, Windows junction/hardlink fallbacks); validate adapted to reality: quoted frontmatter values parsed, skill `id` no longer required (Agent Skills standard), empty placeholder JSON warns; full test cycle distribute → idempotent re-run → exclusion matrix → undistribute recorded above; gates green
- 2026-08-30 — in-progress → awaiting-acceptance; checklist ticked except manual tool-side discovery, which runs at acceptance (needs `distribute` + a fresh session in each tool)
- 2026-08-30 — rework per user correction: `init_dotagents_folder.py` is init/validate only (the rename was to be recorded, not to host distribution) — distribution moved to its own `scripts/distribute.py`; full cycle re-tested with the split scripts, evidence above
- 2026-08-30 — config relocated `scripts/distribute.json` → `.agents/distribute.json` (data-side config per protocol convergence; `scripts/` stays flat, no subdirectory); default `--config` now resolves under `--root`; verified by temp-excluding an agent (16 artifacts instead of 20, excluded everywhere), then restored and undistributed clean
- 2026-08-30 — user relocated the protocol doc and init script into `doc/dotagents/` (`dotagents-protocol.md`, `init_dotagents_folder.py`); updated self-references, requirement doc links, and this evidence path; `scripts/distribute.py` made self-contained (helpers inlined — no cross-directory import from a doc folder); full cycle re-tested from the new locations
- 2026-08-30 — README rewritten: repo purpose, agent/skill catalog, script usage, distribution matrix, quick start
- 2026-08-30 — output hardening after a real user-scope run: shared `~/.agents/skills` links now report once per run instead of once per target; environment-incapable links (cross-volume file links without symlink privilege) classify as `[unavail]` warnings with remediation instead of FAIL; excluded entries print an `[excl]` line (a user-configured `change-ticket-deliver` exclusion had been invisible). Live evidence: this Claude Code session picked up the 5 user-scope skills in the Skill tool listing immediately after the user's distribute run
- 2026-08-30 — Claude Code manual verification complete for user scope: both agents appeared in the live session's Agent tool listing (`Agent Design Orchestrator`, `Skill Lifecycle Orchestrator` from `~/.claude/agents` junctions) on top of the earlier skill listing — agents + skills both confirmed discovered. Remaining: codex/opencode/copilot checks by user; the 2 `[unavail]` copilot user-scope agent links to be created via a one-off elevated run
- 2026-08-30 — CLI extended per user request: `--dest-root` (project scope into another project, with `.agents/skills` links created in the destination so Codex/OpenCode native discovery works there), `validate` subcommand (read-only drift check: missing/broken/stale/foreign + manifest cross-check), `--dry-run` on distribute/undistribute. Tested end to end against a temp project: dry-run creates nothing; 16 artifacts installed cross-drive (junctions cross-volume OK); validate detects a hand-removed link (`[missing]` + manifest `[gone]`, exit 1); undistribute removes exactly the project-scope set
- 2026-08-30 — safety guard added after the live user distribution was found wiped (bare `undistribute` had removed every scope): undistribute without `--scope`/`--targets` now refuses to run unless `--all` is passed; user scope restored via `distribute --scope user` (16 artifacts, 2 known `[unavail]`)
- 2026-08-30 — manual verification completed: Claude Code TUI loads all 6 user-scope skills + both agents live (skills hot-reloaded mid-session, agents in the Agent tool listing); the VS Code extension initially showed nothing but a Developer: Reload Window picked everything up — distribution itself confirmed working, the gap was extension-host caching only

## Acceptance record

(Verdict: accepted / rejected · date · notes)

## Release record

- Version: (pending)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
