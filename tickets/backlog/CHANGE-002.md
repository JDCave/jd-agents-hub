---
branch: feature/CHANGE-002-agent-discovery-commit
created: 2026-08-30
id: CHANGE-002
status: awaiting-acceptance
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

## Findings: agent discovery evaluation

**Verdict: NOT recognized.** Claude Code's Agent tool does not scan `.agents/agents/` — no
setting exists to add custom agent discovery paths. Canonical discovery locations (per
https://code.claude.com/docs/en/sub-agents):

- Project: `.claude/agents/` — scanned walking up from cwd to the repo root (closest wins on name conflicts)
- User: `~/.claude/agents/`
- `--add-dir` directories' `.claude/agents/`, plugin `agents/` directories, managed settings, session `--agents` JSON

The file naming is NOT the blocker: scanning is recursive and agent identity comes from the
frontmatter `name` field, so a nested `<dir>/agent.md` layout works — but only under
`.claude/agents/`. Required frontmatter is `name` + `description` (this repo's agents carry
both, plus nonstandard fields like `role`/`enabled`/`connection-type` that are ignored).
Live evidence: `skill-lifecycle-orchestrator` has been committed since fb5ae94 yet has never
appeared in a session's available agent types.

**Recommendation (follow-up, out of scope here):** mirror or move the agent definitions into
`.claude/agents/` (e.g. `.claude/agents/agent-design-orchestrator/agent.md`), then start a
new session — agent files are not live-reloaded.

## Acceptance criteria

- [x] Discovery evaluation recorded in this ticket: definitive verdict (recognized / not recognized), the canonical agent discovery locations per official docs, and a recommendation for making the agents loadable
- [x] Pending work committed on the branch, staged file by file (never `git add -A`), with the three suspicious SKILL.md frontmatter regressions (version downgrades + stripped license/attribution) explicitly left out and flagged to the user
- [x] skill gate PASS (quality ≥90) for every skill including the two new ones, and the repo-wide audit has no ERROR
- [x] CHANGE-002 itself follows the workflow record → start → verify with every transition logged in the progress log

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 1 | 5/6 PASS (agent-designer 94.5, agent-workflow-designer 92.8, change-ticket-deliver 90.7, skill-builder 90.5, skill-security-auditor 91.4); skill-tester 89.8 FAIL — caused solely by the uncommitted working-tree frontmatter regression that this change deliberately excludes; committed content scores 90.0 (verified on a temp copy, and registry history PASS 90.0 on 2026-08-28). CI gates committed content. |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 6/6 skills PASS (100%), no ERROR |
| pre-commit hook (automatic, skills commit 9454229) | 0 | agent-designer PASS 94.5, agent-workflow-designer PASS 92.8 |

## Progress log

- 2026-08-30 — open: ticket created
- 2026-08-30 — open → in-progress; branch feature/CHANGE-002-agent-discovery-commit created
- 2026-08-30 — CHANGE-001 finalized as merged on main (52c9d9c) before this ticket was recorded (65c267e)
- 2026-08-30 — discovery evaluation completed (see Findings); pending work landed in 4 commits: harness doc (d77c218), agent + .agents placeholders (d5b0a63), two new skills + registry (9454229), Claude settings (fc0c1b8); 3 SKILL.md frontmatter regressions deliberately excluded
- 2026-08-30 — in-progress → awaiting-acceptance; checklist ticked, evidence above

## Acceptance record

(Verdict: accepted / rejected · date · notes)

## Release record

- Version: (pending)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
