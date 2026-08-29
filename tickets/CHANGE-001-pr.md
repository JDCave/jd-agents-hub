## Summary

[CHANGE-001] Add change ticket management workflow

## What & why

The repo had no mechanism for tracking problems and ideas. This adds a ticket-driven
workflow: every reported problem or proposed idea becomes a numbered markdown ticket
(`tickets/CHANGE-NNN.md`) that drives a branch → verify → user acceptance → semver
tag → PR lifecycle, aligned with doc/harness-engineering.md (ticket = State,
acceptance checklist = Scope, repo gates = Verification). Includes the deterministic
`ticket_utils.py` helpers (new-ticket / next-id / next-version), a root CHANGELOG.md
maintained at tag time, and 11 unit tests.

## Acceptance criteria

- [x] `.agents/skills/change-management/` is structurally complete (SKILL.md ≤100 lines + scripts/assets/references/examples/expected_outputs/tests)
- [x] skill_gate verdicts PASS for change-management (quality ≥90) and the repo-wide audit_skills run has no ERROR
- [x] All three ticket_utils.py subcommands work and unit tests pass
- [x] CHANGE-001 itself follows the workflow through record → start → verify → accept, every transition logged
- [x] A root CHANGELOG.md is maintained at accept-and-tag time

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/change-management | 0 | PASS (quality 91.3/90, all 8 checks green) |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 6 skills all 6/6, no ERROR |
| python -m unittest discover -s tests (inside change-management) | 0 | 11/11 OK |

## Release

- tag: v0.1.0 (annotated, on this branch)
- ticket: tickets/CHANGE-001.md
