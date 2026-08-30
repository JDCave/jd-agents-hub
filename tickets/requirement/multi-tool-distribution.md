# Requirement Analysis: Multi-Tool Distribution of Agents and Skills

- **Date**: 2026-08-30
- **Status**: Draft (requirements analysis only — no ticket opened)
- **Scope**: Distribute the SSOT `.agents/agents/` and `.agents/skills/` content to Claude Code, Codex, OpenCode, and GitHub Copilot (VS Code), via symlinks where formats are compatible and generated files where they are not.

---

## 1. Background

This repo (`jd-agents-hub`) manages personal and open-source agents and skills under
`.agents/` following the dotagents protocol (`doc/dotagents-protocol.md`). The SSOT
layouts are:

- Agents: `.agents/agents/<name>/agent.md` (frontmatter + system prompt)
- Skills: `.agents/skills/<name>/SKILL.md` (+ optional `references/`, `scripts/`, `assets/`)

CHANGE-002 established that no AI tool reads `.agents/agents/` for agents natively.
We need a distribution mechanism so every supported tool can discover these
definitions, while `.agents/` remains the single source of truth.

## 2. Problem statement

Each target tool has its own discovery paths and file formats for agents. Skills are
better standardized, but at least Claude Code requires a separate location. A
per-tool adapter layer is needed that is repeatable, idempotent, and reversible, and
that supports excluding selected agents/skills from installation.

## 3. Research findings (verified 2026-08-30, official docs)

### 3.1 Agents

| Tool | Discovery path | Format | SSOT `<dir>/agent.md` usable as-is? | Strategy |
| --- | --- | --- | --- | --- |
| Claude Code | `.claude/agents/` (project, recursive) / `~/.claude/agents/` | .md + YAML frontmatter; `name` + `description` required; identity from frontmatter `name` only; unknown keys ignored; `name` must not start with `-` or contain `:` | **Yes** (symlink the directory) | Symlink |
| Copilot (VS Code / GitHub) | `.github/agents/` (any `.md` detected; `.agent.md` is convention); also natively reads `.claude/agents/` in Claude format | .md + frontmatter; `name` falls back to filename | Yes (must link as `<name>.md`, not `agent.md`; or reuse the Claude mirror) | Symlink |
| OpenCode | `.opencode/agents/` (project; current docs use plural — older releases used `agent/`) / `~/.config/opencode/agents/` | .md; **filename = agent name**; `description` required; unknown frontmatter keys are passed through to the provider as model options (must be stripped) | No — all would collide on the name `agent` | Generate `<name>.md` (filtered frontmatter, add `mode: subagent`) |
| Codex | `.codex/agents/` (project) / `~/.codex/agents/` (personal) | **TOML**; required `name`, `description`, `developer_instructions` (= system prompt body as multi-line string); `name` is the source of truth | No (different format) | Generate `<name>.toml` |

Sources: https://code.claude.com/docs/en/sub-agents ·
https://code.visualstudio.com/docs/agent-customization/custom-agents ·
https://opencode.ai/docs/agents/ ·
https://learn.chatgpt.com/docs/agent-configuration/subagents

### 3.2 Skills

`.agents/skills/<name>/SKILL.md` is the de-facto cross-tool standard (Agent Skills
open standard). Codex and OpenCode read it natively — zero distribution needed.

| Tool | Project level | User level | Reads `.agents/skills/`? |
| --- | --- | --- | --- |
| Codex | `.agents/skills/` (scanned from cwd upward) | `~/.agents/skills` | **Yes — no distribution** |
| OpenCode | `.agents/skills/`, `.claude/skills/`, `.opencode/skills/` | `~/.agents/skills`, `~/.claude/skills`, `~/.config/opencode/skills` | **Yes — no distribution** |
| Copilot | `.github/skills/<name>/` (also reads `.claude/skills/`) | `~/.agents/skills`, `~/.copilot/skills` | Project: no (symlink to `.github/skills/`); user: yes |
| Claude Code | `.claude/skills/<name>/SKILL.md` | `~/.claude/skills/` | No — symlink (**officially supported**: a skill entry may be a symlink to a directory; the same target reached via multiple paths is loaded once) |

Cross-tool rules:

- Skill frontmatter `name` must match the directory name, lowercase kebab-case,
  1–64 chars (OpenCode enforces; Claude derives the command from the directory name).
- `description` is required (1–1024 chars).
- Stick to standard frontmatter fields (`name`, `description`, `license`,
  `compatibility`, `metadata`) for portability; unknown fields are ignored by
  OpenCode but hard-fail when uploaded to claude.ai.

Sources: https://code.claude.com/docs/en/skills ·
https://opencode.ai/docs/skills/ ·
https://learn.chatgpt.com/docs/build-skills ·
https://code.visualstudio.com/docs/agent-customization/agent-skills

## 4. Goals

1. One command installs all (non-excluded) agents and skills into every supported tool.
2. `.agents/` stays the SSOT — adapters never modify it; generated files are marked
   auto-generated and never hand-edited.
3. Distribution is idempotent (re-running produces no changes) and reversible
   (an undistribute removes exactly what was created).
4. An exclusion list prevents selected agents/skills from being installed, globally
   or per tool.

## 5. Non-goals

- Bidirectional sync (editing generated files and copying back).
- Distributing other `.agents/` content (mcp.json, tasks, memories, AGENTS.md) —
  may become follow-up tickets.
- CI automation of distribution (local, on-demand command only).

## 6. Functional requirements

| # | Requirement |
| --- | --- |
| FR1 | `distribute` command in its own script `scripts/distribute.py` (`init_dotagents_folder.py` stays init/validate-only) that installs agents and skills for a selectable target set: `claude`, `codex`, `opencode`, `copilot` (default: all present on the machine) |
| FR2 | Per-target strategy per the matrix in §3: skills → symlinked directories; agents → symlink (Claude, Copilot) or generated files (OpenCode `<name>.md`, Codex `<name>.toml`) |
| FR3 | Exclusion config: named agents/skills skipped globally, optionally per target; see open questions for file location |
| FR4 | Generated files carry a first-line comment identifying them as auto-generated from the SSOT path |
| FR5 | `undistribute` command removes exactly the links/files created earlier (tracked via a manifest, e.g. `.agents/.backups/`-adjacent state file), and reports foreign files it refuses to touch |
| FR6 | Drift detection: report broken links, SSOT entries missing a manifest record, and manifest entries whose SSOT source disappeared |
| FR7 | `validate` extends to check cross-tool portability: skill `name` matches directory (lowercase kebab), agent `name` is kebab-case, frontmatter parses, description present |

## 7. Non-functional requirements

- Python 3.8+, standard library only (matches the rest of `scripts/`); Windows / macOS / Linux.
- Windows: directory symlinks need Developer Mode or admin; fall back to junctions
  (`mklink /J`) for directories and document the requirement for file links.
- Atomic writes (temp file + rename) for generated files, consistent with the protocol.
- No network access; all operations local.

## 8. Decisions (resolved 2026-08-30, recorded in CHANGE-003)

1. **Distribution scope** — *decided*: both, user-selectable per run via `--scope {project,user}`, default `project`. Project mode writes the repo-local tool directories; user mode writes the home-level locations (`~/.claude/`, `~/.copilot/`, `~/.codex/`, `~/.config/opencode/`, and the shared `~/.agents/skills/` which serves Codex, OpenCode, and Copilot user-level skill discovery natively).
2. **Exclusion config location** — *decided, amended same day*: `.agents/distribute.json` in the project root — the config filters SSOT content, so it belongs with the data under the protocol's `.agents/` convergence, decoupled from script location. (Initial decision was `scripts/distribute.json` next to the script; relocated per review discussion. `scripts/` stays flat — no `distribute/` subdirectory while distribution is a single script.)
3. **OpenCode directory name** — *decided*: configurable via the exclusion/config file (`opencode.agents_dir`, default `agents` per the 2026-08 docs; older releases used the singular `agent/`).
4. **SSOT frontmatter normalization** — *decided*: no normalization in this change. `validate` reports non-kebab agent `name` values as warnings (portability guidance); adapters derive generated/symlinked identities from the directory name, so display-style names stay functional everywhere.
5. **Copilot via `.claude/agents` reuse** — *decided*: no coupling — the Copilot target owns its `.github/agents/<name>.md` links (project) / `~/.copilot/agents/<name>.md` (user) regardless of whether the Claude target is enabled.

## 9. Draft acceptance criteria (input for a future ticket)

- [ ] After `distribute`, each installed tool discovers every non-excluded agent and skill (manual verification checklist per tool: `/agents` + `/skills` in Claude Code, agent picker in VS Code, `@` mention in OpenCode, agent mention in Codex)
- [ ] Excluded entries are absent from all targets
- [ ] Re-running `distribute` makes no changes (idempotent)
- [ ] `undistribute` removes exactly what was created; the working tree returns to its prior state
- [ ] SSOT files are byte-identical before and after (`git status` clean in `.agents/`)
- [ ] Generated files (OpenCode `.md`, Codex `.toml`) carry the auto-generated marker and correctly filtered frontmatter
- [ ] `validate` reports the portability checks of FR7 with no errors on this repo

## 10. Suggested file/directory conventions

- Requirement analyses live in `tickets/requirement/` (this document establishes the
  convention); file name is a kebab-case slug of the topic, no ticket number — the
  number is assigned when a ticket is opened and may reference this document.
