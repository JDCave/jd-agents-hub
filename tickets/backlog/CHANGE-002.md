---
branch: (none)
created: 2026-08-30
id: CHANGE-002
status: open
tag: (none)
title: Evaluate .agents agents discovery and commit pending repo work
type: idea
updated: 2026-08-30
---

## Description

Two-part housekeeping change:

1. **Agent discovery evaluation.** Agents live in this repo as
   `.agents/agents/<name>/agent.md` (`skill-lifecycle-orchestrator` already committed,
   `agent-design-orchestrator` pending). In a live Claude Code session in this repo,
   none of them appear in the Agent tool's available agent types. Evaluate whether this
   layout can be recognized by the Agent tool, establish the canonical discovery
   locations, and record a recommendation for making these agents loadable.

2. **Land pending uncommitted work.** The repo has accumulated uncommitted work:
   new skills `agent-designer` and `agent-workflow-designer`, the
   `agent-design-orchestrator` agent, harness files (`.agents/models.json`,
   `.agents/system-prompt.md`), `doc/harness-engineering.md`, `.claude/settings.json`,
   and the hook-updated `.agents/skills/registry.json`. Commit them through this
   workflow with the skill gate green, staging explicit paths only.

## Acceptance criteria

- [ ] Discovery evaluation recorded in this ticket: definitive verdict (recognized / not recognized), the canonical agent discovery locations per official docs, and a recommendation for making the agents loadable
- [ ] Pending work committed on the branch, staged file by file (never `git add -A`), with the three suspicious SKILL.md frontmatter regressions (version downgrades + stripped license/attribution) explicitly left out and flagged to the user
- [ ] skill gate PASS (quality ≥90) for every skill including the two new ones, and the repo-wide audit has no ERROR
- [ ] CHANGE-002 itself follows the workflow record → start → verify with every transition logged in the progress log

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
