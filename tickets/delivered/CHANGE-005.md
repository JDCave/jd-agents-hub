---
branch: feature/CHANGE-005-spec-kit-absorption
created: 2026-11-25
id: CHANGE-005
status: delivered
tag: v0.5.0
title: spec-kit skill absorption
type: idea
updated: 2026-11-25
---

## Description

Absorb GitHub spec-kit's process skills into the hub's `.agents/` SSOT as three
hub-native skills, so `scripts/distribute.py` can publish them to Claude Code,
Codex, OpenCode, and Copilot like every other hub skill.

spec-kit ships three independent processes as command templates rendered into
skill files: core spec-driven development (constitution → specify → clarify →
plan → checklist → tasks → analyze → implement → converge), bug triage
(assess → fix → test), and idea assessment (intake → research → define → shape →
decide). This change ports the process content — gates, artifact schemas, caps,
verdict vocabularies, and the `.specify/` on-disk contract — while dropping the
`specify` CLI, integrations, presets, extension hooks, catalogs, workflows, and
the git extension (the hub's change workflow already owns branch/commit/PR).

The three new skills are:

- `spec-driven-development` — 9-step router with per-step references, five ported
  page templates, and `scripts/sdd_workflow.py` (bootstrap, new-feature,
  prereqs, plan, tasks, status, resolve-template).
- `bugfix-triage` — assess/fix/test references, report templates, and
  `scripts/bug_workflow.py` (slug normalization, uniqueness, path safety,
  report scaffolding, verdict validation).
- `idea-assessment` — five stage references, stage templates, and
  `scripts/assess_workflow.py` (slug/path safety, stage scaffolding, funnel
  preconditions, verdict validation and downgrade).

The implementation is already present in the working tree from the earlier
analysis session (2026-11-08) and verified again for this ticket. This ticket
records, verifies, and delivers it through the repo's change workflow.

Source: `D:\workspace\code\opensource\github\spec-kit` at commit
`c43849408ac0de2ca6a52f14eaae71449776057b` (MIT, Copyright GitHub, Inc.).
Ported material and attribution are documented in each skill's
`references/upstream.md`.

**Out of scope** (pre-existing, unrelated working-tree changes left untouched by
this ticket): the untracked `caveman` skill, the seven untracked `speckit-*`
native skills, local edits to `skill-tester` scripts
(`script_tester.py`, `security_scorer.py`), the deletion of
`.github/workflows/skill-gate.yml`, and the `skill-builder/SKILL.md` attribution
edit. None of these are staged or committed here.

## Acceptance criteria

- [x] Three skills committed under `.agents/skills/{spec-driven-development,bugfix-triage,idea-assessment}/`, each with SKILL.md, README.md, flat references/, assets/, expected_outputs/, stdlib scripts/, and tests/ — no `__pycache__` or stray files
- [x] `skill_gate.py <skill> --json` returns PASS with 8/8 checks and quality ≥ 90 for each of the three skills
- [x] Unit suites pass: `python -m unittest discover -s .agents/skills/<skill>/tests` (32 + 29 + 27 tests, all OK)
- [x] `registry.json` carries the three new entries (`status: draft` + `last_gate` PASS/score), and no out-of-scope entry is committed
- [x] `README.md` skills catalog lists the three skills
- [x] Requirement analysis `tickets/requirement/spec-kit-absorption.md` committed alongside
- [x] `python docs/dotagents/init_dotagents_folder.py validate --root .` exits 0 with no new errors or warnings caused by this change
- [x] `python scripts/distribute.py distribute --dry-run` reports 0 conflicts and would install the three skills
- [x] Scope guard: the pre-existing out-of-scope working-tree changes remain uncommitted and unmodified

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/spec-driven-development --json | 0 | PASS, 8/8 checks, quality 98.9 (Docs 96.6 · Code 98.0 · Complete 100 · Security 100 · Usability 100) |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/bugfix-triage --json | 0 | PASS, 8/8 checks, quality 98.3 (Docs 98.3 · Code 98.0 · Complete 100 · Security 100 · Usability 95.0) |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/idea-assessment --json | 0 | PASS, 8/8 checks, quality 97.9 (Docs 96.5 · Code 98.0 · Complete 100 · Security 100 · Usability 95.0) |
| python -m unittest discover -s .agents/skills/spec-driven-development/tests | 0 | Ran 32 tests, OK |
| python -m unittest discover -s .agents/skills/bugfix-triage/tests | 0 | Ran 29 tests, OK |
| python -m unittest discover -s .agents/skills/idea-assessment/tests | 0 | Ran 27 tests, OK |
| python docs/dotagents/init_dotagents_folder.py validate --root . | 0 | OK: 82 file(s) valid, 3 warning(s) — all pre-existing (empty models.json placeholder; 2 non-kebab agent names, CHANGE-003 decision); no new warnings from this change |
| python scripts/distribute.py distribute --dry-run | 0 | 31 new, 0 updated, 13 unchanged, 36 native, 0 unavailable, 0 conflicts (31 includes pre-existing untracked caveman/speckit-* skills; the three CHANGE-005 skills link into `.claude/skills/` and `.github/skills/` and are native for Codex/OpenCode) |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 18 SKILL.md audited, 11 PASS (6/6), 0 ERROR — the 7 non-passing are the pre-existing untracked `speckit-*` skills, out of scope |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 1 | 11/18 pass; BLOCKED: 7 pre-existing untracked `speckit-*` skills only (out of scope). All 10 committed skills (7 existing + 3 from CHANGE-005) pass; CI gates the committed tree, so the PR gate is expected to pass |

## Progress log

- 2026-11-25 — open: ticket created; the three skills and supporting files already
  exist in the working tree from the 2026-11-08 analysis session, re-gated before
  recording
- 2026-11-25 — open → in-progress: branch `feature/CHANGE-005-spec-kit-absorption`
  created; scope = the three absorbed skills + README/registry/requirement analysis
  only (pre-existing unrelated working-tree changes stay out)
- 2026-11-25 — work + verify: three skills re-gated (PASS 8/8, quality 98.9/98.3/97.9),
  unit suites 32+29+27 OK, SSOT validate clean, distribution dry-run 0 conflicts;
  registry entries recorded; accepted scope guard verified. No code changes were
  needed beyond the 2026-11-08 implementation.
- 2026-11-25 — in-progress → awaiting-acceptance: checklist ticked, evidence recorded,
  awaiting explicit user acceptance before tag/push/PR
- 2026-11-25 — awaiting-acceptance → accepted: explicit user acceptance; annotated tag
  `v0.5.0` created on this commit, CHANGELOG `[v0.5.0]` section added
- 2026-11-25 — accepted → delivered: ticket moved to `tickets/delivered/`, branch and
  tag pushed to origin, PR opened to `main`
- 2026-11-25 — PR #6 opened (https://github.com/JDCave/jd-agents-hub/pull/6); waiting
  for the CI skill-gate and user merge decision
- 2026-11-08 — prior session: analysis of spec-kit's 17 command-skills, porting
  strategy, and implementation of the three hub skills (quality 99.0 / 98.3 / 97.9
  at that time)

## Acceptance record

Verdict: **accepted** · 2026-11-25 · user accepted through the session acceptance
prompt after reviewing the checklist and verification evidence above; no changes
requested.

## Release record

- Version: v0.5.0
- Tag: v0.5.0 (annotated, on the `feature/CHANGE-005-spec-kit-absorption` branch)
- PR: #6 — https://github.com/JDCave/jd-agents-hub/pull/6
- Merged: (pending)
