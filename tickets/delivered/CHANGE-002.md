---
branch: feature/CHANGE-002-agent-discovery-commit
created: 2026-08-30
id: CHANGE-002
status: accepted
tag: v0.2.0
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
   `.agents/system-prompt.md`), `doc/harness-engineering.md`,
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
- [x] Pending work committed on the branch, staged file by file (never `git add -A`); per user decision at first review, the 3 SKILL.md frontmatter resets (version 1.0.0 baseline, license/attribution removed) are intentional and included as-is
- [x] skill gate PASS (quality ≥90) for every skill including the two new ones, and the repo-wide audit has no ERROR
- [x] CHANGE-002 itself follows the workflow record → start → verify with every transition logged in the progress log

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 0 | 6/6 PASS after rework (agent-designer 94.5, agent-workflow-designer 92.8, change-ticket-deliver 90.7, skill-builder 90.5, skill-security-auditor 91.4, skill-tester 90.1) |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 6/6 skills PASS (100%), no ERROR |
| pre-commit hook (automatic, commits 9454229 + 617d401) | 0 | agent-designer 94.5, agent-workflow-designer 92.8, skill-builder 90.5, skill-security-auditor 91.4, skill-tester 90.1 — all PASS |
| First-review run (superseded, kept for the record) | 1 | skill_gate --all was 5/6 with skill-tester 89.8 while the SKILL.md resets sat uncommitted in the working tree; committed content then scored 90.0. After the resets were committed per user decision (617d401), skill-tester scores 90.1 with a When to Use section added to stay ≥90 without restoring the removed frontmatter |

## Progress log

- 2026-08-30 — open: ticket created
- 2026-08-30 — open → in-progress; branch feature/CHANGE-002-agent-discovery-commit created
- 2026-08-30 — CHANGE-001 finalized as merged on main (52c9d9c) before this ticket was recorded (65c267e)
- 2026-08-30 — discovery evaluation completed (see Findings); pending work landed in 3 commits: harness doc (d77c218), agent + .agents placeholders (d5b0a63), two new skills + registry (9454229); the 3 SKILL.md frontmatter resets were deliberately excluded at first review
- 2026-08-30 — in-progress → awaiting-acceptance; checklist ticked, evidence above
- 2026-08-30 — awaiting-acceptance → in-progress; user rejected: the 3 SKILL.md frontmatter changes are intentional (own baseline, attribution removed on purpose) and must be committed as part of this change
- 2026-08-30 — scope updated per rejection: SKILL.md resets now included as-is; acceptance criterion 2 reworded accordingly
- 2026-08-30 — SKILL.md resets committed (617d401); the pre-commit gate initially blocked skill-tester at 89.8, resolved by adding a When to Use section (SKILL.md now 99 lines) without touching the reset frontmatter; skill_gate --all now 6/6 PASS
- 2026-08-30 — in-progress → awaiting-acceptance (second review); evidence refreshed above
- 2026-08-30 — user decision at accept time: `.claude/` stays out of the repo — its commit was dropped from the unpushed branch via rebase and `.claude/` was added to .gitignore
- 2026-08-30 — awaiting-acceptance → accepted; user approved via interactive prompt; tagged v0.2.0

## Acceptance record

Accepted · 2026-08-30 · user approved second review via interactive prompt (accept + tag + push + PR). First review rejected to include the SKILL.md resets — see 2026-08-30 rejection entry in the progress log.

## Release record

- Version: v0.2.0 (idea → minor)
- Tag: v0.2.0 — annotated on the acceptance commit on feature/CHANGE-002-agent-discovery-commit
- PR: (pending)
- Merged: (pending)
