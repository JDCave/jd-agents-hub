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
├── distribute.json          # distribution config: defaults + exclusions
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
python scripts/distribute.py undistribute

# user scope: home-level (~/.claude/, ~/.copilot/, ~/.codex/, ~/.agents/, ...)
python scripts/distribute.py distribute --scope user
python scripts/distribute.py undistribute --scope user

# pick targets / a different config
python scripts/distribute.py distribute --targets claude,copilot
python scripts/distribute.py distribute --config path/to/config.json
```

Options (same for `distribute` and `undistribute`):

| Option | Values | Meaning |
| --- | --- | --- |
| `--scope` | `project` \| `user` | `project` writes repo-local tool dirs (default); `user` writes home-level locations available in every project. |
| `--targets` | any subset of `claude`, `codex`, `opencode`, `copilot` (comma-separated) | Which tools to install for. Default: `default_targets` in `.agents/distribute.json` (all four). |
| `--config` | filesystem path | Config file to use. Default: `.agents/distribute.json` under `--root`. |
| `--root` | filesystem path | Project root that holds `.agents/`. Default: current working directory. |

How each tool is served:

| Tool | Agents | Skills |
| --- | --- | --- |
| Claude Code | link into `.claude/agents/` | link into `.claude/skills/` |
| Copilot (VS Code) | link `.github/agents/<name>.md` (project) / `~/.copilot/agents/` (user) | link `.github/skills/` (project) / shared `~/.agents/skills/` (user) |
| OpenCode | generated `<name>.md` (filename = agent name) | **native** — reads `.agents/skills/` directly |
| Codex | generated `<name>.toml` | **native** — reads `.agents/skills/` directly |

On Windows without symlink privilege, directory links fall back to junctions
and file links to same-volume hardlinks — no Developer Mode needed. 🪟

Exclusions and defaults live in `.agents/distribute.json`:

```json
{
  "default_scope": "project",
  "exclude": {
    "agents": ["agent-you-dont-want"],
    "skills": [],
    "per_target": { "codex": { "skills": ["skill-not-for-codex"] } }
  }
}
```

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
