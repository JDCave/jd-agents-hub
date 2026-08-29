---
branch: feature/CHANGE-001-change-management-skill
created: 2026-08-29
id: CHANGE-001
status: awaiting-acceptance
tag: (none)
title: Add change ticket management workflow
type: idea
updated: 2026-08-29
---

## Description

This repo needs a management mechanism for problems and ideas: when the user reports a
**problem** (a bug hit while using agents/skills) or proposes an **idea** (a new
requirement), record it as a numbered markdown ticket (`tickets/CHANGE-NNN.md`), then
create a `feature/CHANGE-NNN-xxx` branch to fix or implement it, verify with the repo
skill gate, and after user acceptance tag a semantic version (first tag v0.1.0;
problem = patch bump, idea = minor bump), finally opening a PR back to main via the gh
CLI. The whole flow must align with the five subsystems of doc/harness-engineering.md
(ticket = State, acceptance criteria = Scope, gates = Verification, SKILL.md =
Instructions, resume-by-ticket = Session Lifecycle).

## Acceptance criteria

- [x] `.agents/skills/change-management/` is structurally complete (SKILL.md ≤100 lines + scripts/assets/references/examples/expected_outputs/tests)
- [x] skill_gate verdicts PASS for change-management (quality ≥90) and the repo-wide audit_skills run has no ERROR
- [x] All three ticket_utils.py subcommands work (new-ticket / next-id / next-version) and unit tests pass
- [x] CHANGE-001 itself follows the workflow through record → start → verify, with every transition logged in the progress log
- [x] A root CHANGELOG.md is maintained at accept-and-tag time (Keep a Changelog style, one entry per version, referencing the ticket id)

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/change-management --update-registry | 0 | PASS (quality 91.3/90, all 8 checks green) |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 6 skills all 6/6, no ERROR |
| python -m unittest discover -s tests (inside change-management) | 0 | 11/11 OK |

## Progress log

- 2026-08-29 — open: ticket created
- 2026-08-29 — open → in-progress; branch feature/CHANGE-001-change-management-skill created
- 2026-08-29 — in-progress → awaiting-acceptance; skill committed (pre-commit gate passed automatically), evidence above
- 2026-08-29 — scope extended with the CHANGELOG.md mechanism per user request (maintained at tag time); gate re-run PASS 91.3
- 2026-08-29 — ticket content converted to English per user request; gates re-run green

## Acceptance record

(Awaiting user acceptance: verdict / date / notes)

## Release record

- Version: (pending, expected v0.1.0 from next-version after acceptance)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
