# .agents Protocol — The Open Standard for AI Agent Configuration

> **Source**: <https://dotagentsprotocol.com/>
>
> **Status**: Draft · 2026-02-24

---

## 1. Core Concept

The **.agents Protocol** is an open directory convention that unifies AI agent configuration into **one vendor-neutral, version-controllable location** (`.agents/`). It consolidates MCP tools, AGENTS.md instructions, Skills, Sub-Agents, Tasks, Memories, and model config into plain files.

---

## 2. The Problem vs. The Solution

| Fragmentation (Problem) | Convergence (Solution) |
|---|---|
| Config scattered across `.cursor/`, `.claude/`, `.github/copilot-instructions.md` | Single `.agents/` directory houses everything |
| Vendor lock-in; no portability | Vendor-neutral — works with any AI tool |
| Agent knowledge lost between sessions/tools | Persistent memories and skills |
| Cannot version-control complete agent setups | Git-friendly — commit, diff, branch, and share |

---

## 3. Ecosystem Convergence (7 Open Standards)

The `.agents/` directory acts as a convergence point (**not a replacement**) for 7 open standards:

| Standard | Steward | Purpose | Maps to |
|---|---|---|---|
| **MCP** | Anthropic / Linux Foundation | Connect AI to external tools/data (stdio, HTTP, WebSocket) | `mcp.json` |
| **AGENTS.md** | OpenAI / Linux Foundation | Markdown format for guiding coding agents | `agents.md` |
| **Skills** | Anthropic | Codified procedural knowledge (instruction files) | `skills/*/skill.md` |
| **ACP** | Zed Industries | Standard for agent-to-editor communication | `agent profiles` |
| **Sub-Agents** | .agents Protocol | Declarative sub-agent profiles for task delegation | `agents/*/agent.md` |
| **Tasks** | .agents Protocol | Scheduled repeat tasks with interval triggers | `tasks/*/task.md` |
| **Memories** | .agents Protocol | Structured memory entries persisting across sessions | `memories/*.md` |

---

## 4. Directory Structure & Layering

The protocol uses a **two-layer overlay system** where the workspace overrides the global layer.

**Merge Order:** `defaults` ← `config.json` ← `~/.agents` ← `./.agents`

- **JSON**: shallow-merge by key
- **Skills / memories / agents / tasks**: merge by ID (workspace always wins)

### Full Layout

```text
.agents/
├── speakmcp-settings.json  # general settings
├── mcp.json                # MCP servers & tools
├── models.json             # model presets & keys
├── system-prompt.md        # system prompt
├── AGENTS.md               # agent guidelines (AGENTS.md compatible)
├── layouts/
│   └── ui.json             # UI/layout prefs
├── skills/
│   └── code-review/
│       └── SKILL.md        # skill definition
├── agents/
│   └── code-reviewer/
│       ├── agent.md        # profile + system prompt
│       └── config.json     # tool/model/connection config
├── tasks/
│   └── daily-code-review/
│       └── task.md         # repeat task definition
├── memories/
│   ├── arch-decisions.md   # persistent memory
│   └── user-prefs.md
└── .backups/               # auto-rotated backups
```

---

## 5. File Formats & Examples

### Format Rules

- **Config files**: Plain JSON
- **Content files**: Markdown with simple frontmatter (`---` fences with `key: value` lines)
- Frontmatter is **not full YAML** — intentionally avoids external dependencies
- List fields accept CSV (`tags: a, b, c`) or JSON arrays
- Keys are sorted deterministically for clean git diffs

### MCP Configuration (`mcp.json`)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@mcp/server-filesystem"],
      "transport": "stdio"
    },
    "github": {
      "url": "https://api.github.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Skill Definition (`skills/code-review/skill.md`)

```markdown
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
```

### Persistent Memory (`memories/arch-decisions.md`)

```markdown
---
id: arch_001
title: Database Architecture
content: PostgreSQL with Drizzle ORM
importance: high
tags: database, architecture, orm
---

We chose PostgreSQL over MongoDB for
relational data integrity...
```

### Sub-Agent Profile (`agents/code-reviewer/agent.md`)

```markdown
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
```

### Sub-Agent Config (`agents/code-reviewer/config.json`)

```json
{
  "toolConfig": {
    "disabledServers": ["filesystem"],
    "enabledBuiltinTools": ["mark_work_complete"]
  },
  "modelConfig": {
    "mcpToolsProviderId": "openai",
    "mcpToolsOpenaiModel": "gpt-4o"
  },
  "connection": {
    "type": "stdio",
    "command": "my-agent",
    "args": ["--mode", "review"]
  }
}
```

### Scheduled Task (`tasks/daily-code-review/task.md`)

```markdown
---
kind: task
id: daily-code-review
name: Daily Code Review
intervalMinutes: 60
enabled: true
runOnStartup: false
profileId: abc-123
---

Review all open pull requests and
summarize their status.
```

---

## 6. Design Principles

| Principle | Rationale |
|---|---|
| **Human-readable** | Plain JSON and Markdown only. No binary formats or proprietary schemas. |
| **Version-controllable** | Deterministic key sorting ensures clean, minimal git diffs. |
| **Portable** | Relative paths throughout. No vendor lock-in. Copy the directory, and it works everywhere. |
| **Safe by default** | Atomic writes (temp file + rename), timestamped backups, auto-recovery from parse failures. |
| **Extensible** | Add new config files without breaking existing structures. Tools ignore unknown keys. |

---

## 7. .agents Hub (Sharing Ecosystem)

The protocol includes a public catalog called the **.agents Hub** for sharing installable `.dotagents` bundles.

- **Public-safe defaults**: Agents, MCP configs, and skills are shared by default. Memories and repeat tasks are strictly opt-in.
- **Install handoff**: Bundles are downloaded and opened directly via a desktop app.
- **Community-driven**: Anyone can publish, anyone can install.

---

## 8. Getting Started (Quick Implementation)

Adoption is incremental — start with just what you need:

```bash
# 1. Create directories
mkdir -p .agents/skills .agents/agents .agents/tasks .agents/memories

# 2. Add guidelines
#    Drop your AGENTS.md content into .agents/agents.md

# 3. Register MCP tools
#    Add server configs to .agents/mcp.json

# 4. Codify skills
#    Create skills/[name]/skill.md files

# 5. Commit to git
git add .agents/
git commit -m "Add .agents protocol configuration"
```

> **Key insight**: You don't need to adopt everything at once. Start with `agents.md` and `mcp.json`, then layer in skills, memories, sub-agents, and tasks as your workflow matures.
