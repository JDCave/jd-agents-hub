# 🤖 JD Agents Hub

A personal hub for managing and sharing reusable **AI agents** and **skills**.
Everything lives in one vendor-neutral SSOT (`.agents/`, following the
[.agents protocol](doc/dotagents/dotagents-protocol.md)) and gets distributed
to each AI tool's native discovery location via one command — symlink where
formats are compatible, generated files where they are not.

## 📁 Repository Layout

```text
.agents/                     # SSOT — the single source of truth
├── agents/<name>/agent.md   # sub-agent profiles (frontmatter + system prompt)
├── skills/<name>/SKILL.md   # skills (+ references/ scripts/ assets/)
├── distribute.json          # distribution policy: defaults + hub_only set
└── ...
doc/dotagents/               # .agents protocol doc + init/validate script
scripts/distribute.py        # the distribution engine
tickets/                     # change tickets (backlog → delivered) + requirement analyses
```

## 🕵️ Agents

| Agent | Purpose |
| --- | --- |
| `agent-design-orchestrator` | Runs the agent design pipeline end to end — scaffolds the workflow skeleton, fills agent slots, equips agents with validated tool schemas, and loops evaluation until 0 critical issues. |
| `skill-lifecycle-orchestrator` | Gates changed skills, interprets results against the skill-builder doctrine, and drives the improvement roadmap until pass — the standing referee for skill quality. |

## 🧩 Skills

| Skill | Purpose |
| --- | --- |
| `agent-designer` | Design multi-agent systems: orchestration pattern choice (supervisor/swarm/pipeline), provider-ready tool schemas, and execution-log analysis for cost/latency bottlenecks. |
| `agent-workflow-designer` | Architect production-grade multi-agent workflows — sequential/parallel/router/orchestrator/evaluator patterns, handoff contracts, failure handling, and cost/context controls. |
| `change-ticket-deliver` | Full change lifecycle: record numbered tickets, branch, verify via the skill gate, tag accepted changes with semver, and open PRs. |
| `skill-builder` | Create new skills with proper structure, progressive disclosure, and bundled resources. |
| `skill-security-auditor` | Security audit and vulnerability scanner for skills before installation — dangerous Python patterns, prompt injection, exfiltration, and supply-chain risks. |
| `skill-tester` | Validate and score skill quality (structure, scripts, multi-dimensional grading) — also powers the repo's pre-commit gate and CI checks. |

## 🔧 Scripts

### `scripts/distribute.py` — distribution engine 🚚

Installs the SSOT agents/skills into each tool's native discovery location.
Idempotent, reversible (manifest-tracked), and safe: `.agents/` is never
modified, foreign files are never touched.

```bash
# project scope (default): repo-local .claude/, .github/, .codex/, .opencode/
python scripts/distribute.py distribute
python scripts/distribute.py undistribute --scope project

# distribute into ANOTHER project (its tool dirs + .agents/skills links)
python scripts/distribute.py distribute --dest-root d:/code/some-project

# user scope: home-level (~/.claude/, ~/.copilot/, ~/.codex/, ~/.agents/, ...)
python scripts/distribute.py distribute --scope user
python scripts/distribute.py undistribute --scope user

# preview without writing / check drift
python scripts/distribute.py distribute --dry-run
python scripts/distribute.py undistribute --all --dry-run
python scripts/distribute.py validate

# pick targets / a different config
python scripts/distribute.py distribute --targets claude,copilot
python scripts/distribute.py distribute --config path/to/config.json
```

Options:

| Option | Applies to | Values | Meaning |
| --- | --- | --- | --- |
| `--scope` | all | `project` \| `user` | `project` writes the destination project's tool dirs (default); `user` writes home-level locations available in every project. |
| `--dest-root` | distribute, validate | path | Destination project for project scope — defaults to `--root` (the hub itself). When set, Codex/OpenCode skills get `.agents/skills` links in the destination so native discovery works there. |
| `--targets` | all | any subset of `claude`, `codex`, `opencode`, `copilot` (comma-separated) | Which tools to install for. Default: all four. |
| `--dry-run` | distribute, undistribute | flag | Print what would happen — no links, files, or manifest changes. |
| `--all` | undistribute | flag | Remove every manifest entry (both scopes). Required when no `--scope`/`--targets` filter is given — a bare `undistribute` refuses to run as a safety guard. |
| `--config` | all | path | Policy file to use. Default: `.agents/distribute.json` under `--root`. |
| `--root` | all | path | The hub project holding `.agents/`. Default: current working directory. |

`validate` re-derives what should be installed and checks it read-only: missing
links/files, broken links, generated files that drifted from the SSOT
(`[stale]`), foreign files, and manifest entries whose target vanished. Links
that were `[unavail]` during install (cross-volume, no symlink privilege)
appear as `[missing]` — run `validate --targets ...` to narrow the check.

How each tool is served:

| Tool | Agents | Skills |
| --- | --- | --- |
| Claude Code | link into `.claude/agents/` | link into `.claude/skills/` |
| Copilot (VS Code) | link `.github/agents/<name>.md` (project) / `~/.copilot/agents/` (user) | link `.github/skills/` (project) / shared `~/.agents/skills/` (user) |
| OpenCode | generated `<name>.md` (filename = agent name) | **native** — reads `.agents/skills/` directly |
| Codex | generated `<name>.toml` | **native** — reads `.agents/skills/` directly |

On Windows without symlink privilege, directory links fall back to junctions
(works across drives) and file links to same-volume hardlinks — no Developer
Mode needed. 🪟 Cross-volume file links (e.g. user-scope Copilot agents when
the repo sits on another drive) are reported as `[unavail]` with remediation
instead of failing the run; enable Developer Mode and re-run to install them.
Skipped entries print an `[excl]` line so silent skips stay visible.

## ⚙️ Distribution policy

The policy is configurable in one file, [.agents/distribute.json](.agents/distribute.json)
(schema sample: [distribute-config.sample.json](scripts/distribute-config.sample.json)):

| Key | Meaning |
| --- | --- |
| `default_scope` / `default_targets` | CLI defaults (`project` / all four tools). |
| `hub_only.agents` / `hub_only.skills` | Entries that exist to manage THIS repo (skill/ticket/quality tooling). They install only when the hub is distributed into itself — never at user scope, never into another project via `--dest-root`. |

Everything not listed in `hub_only` ships wherever you point the distributor.
`validate` flags `hub_only` names that no longer match an SSOT entry, so renames
and typos can't silently re-ship a management tool. Skipped entries print an
`[excl]` line so silent skips stay visible.

### `doc/dotagents/init_dotagents_folder.py` — init & validate 🧱

Creates and checks the `.agents/` folder itself (kept next to the protocol doc):

```bash
python doc/dotagents/init_dotagents_folder.py init --examples   # scaffold .agents/
python doc/dotagents/init_dotagents_folder.py validate          # structure + portability checks
```

`validate` also enforces cross-tool portability: skill `name` must match its
lowercase-kebab directory name, agent frontmatter must parse with a usable
`name`/`description`, and JSON files must be well-formed.

## 🚀 Quick Start

```bash
git clone <this-repo> && cd jd-agents-hub
python doc/dotagents/init_dotagents_folder.py validate   # sanity-check the SSOT
python scripts/distribute.py distribute                  # install everywhere
```

Then restart/refresh each tool (e.g. Claude Code needs a new session) and
verify: `/agents` + `/skills` in Claude Code, the agent picker in VS Code,
`@` mentions in OpenCode, agent mentions in Codex.

## 🎫 Change Workflow

Changes go through numbered tickets (`tickets/`) — see the
`change-ticket-deliver` skill for the full record → branch → verify → accept →
tag → PR lifecycle. Requirement analyses live in `tickets/requirement/`.
