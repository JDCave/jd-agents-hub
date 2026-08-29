## Summary

[CHANGE-NNN] <title>

## What & why

(Copy or adapt from the ticket's Description: what was done and why.)

## Acceptance criteria

- [x] (Copy the checklist from the ticket, each item ticked)

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 0 | all PASS |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | no ERROR |

## Release

- tag: vX.Y.Z (the acceptance tag for this PR)
- ticket: tickets/CHANGE-NNN.md
