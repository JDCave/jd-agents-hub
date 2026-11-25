---
branch: feature/CHANGE-005-spec-kit-absorption
created: 2026-11-25
id: CHANGE-005
status: in-progress
tag: (none)
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

- [ ] Three skills committed under `.agents/skills/{spec-driven-development,bugfix-triage,idea-assessment}/`, each with SKILL.md, README.md, flat references/, assets/, expected_outputs/, stdlib scripts/, and tests/ — no `__pycache__` or stray files
- [ ] `skill_gate.py <skill> --json` returns PASS with 8/8 checks and quality ≥ 90 for each of the three skills
- [ ] Unit suites pass: `python -m unittest discover -s .agents/skills/<skill>/tests` (32 + 29 + 27 tests, all OK)
- [ ] `registry.json` carries the three new entries (`status: draft` + `last_gate` PASS/score), and no out-of-scope entry is committed
- [ ] `README.md` skills catalog lists the three skills
- [ ] Requirement analysis `tickets/requirement/spec-kit-absorption.md` committed alongside
- [ ] `python docs/dotagents/init_dotagents_folder.py validate --root .` exits 0 with no new errors or warnings caused by this change
- [ ] `python scripts/distribute.py distribute --dry-run` reports 0 conflicts and would install the three skills
- [ ] Scope guard: the pre-existing out-of-scope working-tree changes remain uncommitted and unmodified

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/spec-driven-development --json |  |  |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/bugfix-triage --json |  |  |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/idea-assessment --json |  |  |
| python -m unittest discover -s .agents/skills/spec-driven-development/tests |  |  |
| python -m unittest discover -s .agents/skills/bugfix-triage/tests |  |  |
| python -m unittest discover -s .agents/skills/idea-assessment/tests |  |  |
| python docs/dotagents/init_dotagents_folder.py validate --root . |  |  |
| python scripts/distribute.py distribute --dry-run |  |  |
| python .agents/skills/skill-tester/scripts/audit_skills.py |  |  |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all |  |  |

## Progress log

- 2026-11-25 — open: ticket created; the three skills and supporting files already
  exist in the working tree from the 2026-11-08 analysis session, re-gated before
  recording
- 2026-11-25 — open → in-progress: branch `feature/CHANGE-005-spec-kit-absorption`
  created; scope = the three absorbed skills + README/registry/requirement analysis
  only (pre-existing unrelated working-tree changes stay out)
- 2026-11-08 — prior session: analysis of spec-kit's 17 command-skills, porting
  strategy, and implementation of the three hub skills (quality 99.0 / 98.3 / 97.9
  at that time)

## Acceptance record

(Verdict: accepted / rejected · date · notes)

## Release record

- Version: (pending)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
