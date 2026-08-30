---
branch: feature/CHANGE-002-fix-audit-runner
created: 2026-08-29
id: CHANGE-002
status: awaiting-acceptance
tag: (none)
title: audit script cannot run with wrong repo path
type: problem
updated: 2026-08-29
---

## Description

Running the repo-wide audit fails with FileNotFound: RUNNER points at the source
repo's path instead of the actual location under `.agents/skills/...` in this repo.
Expected: audit works out of the box here.

## Acceptance criteria

- [x] audit_skills.py runs repo-wide without FileNotFound
- [x] Exit code 0 and the aggregate report prints normally

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 5 skills audited, no ERROR |

## Progress log

- 2026-08-29 — open: ticket created
- 2026-08-29 — open → in-progress; branch feature/CHANGE-002-fix-audit-runner created
- 2026-08-29 — in-progress → awaiting-acceptance; gates passed, evidence above

## Acceptance record

(Awaiting user acceptance: verdict / date / notes)

## Release record

- Version: (pending, computed by next-version after acceptance)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
