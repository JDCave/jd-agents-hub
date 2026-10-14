---
branch: feature/CHANGE-004-agent-resume-review
created: 2026-10-14
id: CHANGE-004
status: in-progress
tag: (none)
title: agent-resume-review skill
type: idea
updated: 2026-10-14
---

## Description

Land the pre-built `agent-resume-review` skill (v1.1.0) from the working tree into the `.agents/` SSOT through this workflow — same shape as CHANGE-002 (commit pending repo work under a ticket).

The skill evaluates and rewrites resumes for AI Agent engineering roles, zh and en, in two layers:

1. **Deterministic lint** — `scripts/resume_lint.py` detects the resume language, then scores sections, quantified bullets, weak verbs (参与/协助/participated/assisted), keyword tiers, mastery claims (精通/expert), and one-page length; `--json` for machine-readable output, GBK read fallback, UTF-8 output.
2. **Judgment rubric** — six dimensions (impact, Agent depth, JD fit, structure, credibility, ATS delivery) with a scorecard JSON contract (`expected_outputs/score-card-example.json`); verdict `ready` ≥ 85 / `optimize` 70–84 / `rewrite` < 70, never from the lint score alone.

The optimize workflow maps findings to zh/en rewrite tables, a 7-element project block, and keyword-tier tuning (`references/`), then re-lints to prove the delta. Ships sample resumes (zh/en strong/weak), expected lint outputs, and a unittest suite.

Registry entry recorded (gate PASS 96.1 on 2026-10-13). Not in `hub_only` → default distribution to all targets and scopes.

## Acceptance criteria

- [x] Skill committed under `.agents/skills/agent-resume-review/` (SKILL.md, scripts, tests, references, assets, expected_outputs, README, examples) — no build artifacts (`__pycache__` stays ignored)
- [x] `registry.json` carries the `agent-resume-review` entry with its latest gate result
- [x] Lint demo run exits 0; lint reproduces `expected_outputs/` scores for the four bundled samples (zh/en × strong/weak)
- [x] `python -m unittest discover .agents/skills/agent-resume-review/tests` passes
- [x] `init_dotagents_folder.py validate` clean for the new skill (kebab-case name matches directory, required frontmatter present)
- [x] skill gate PASS (quality ≥90) for all skills and repo-wide audit has no ERROR
- [ ] Manual: after `distribute --scope user`, the skill appears in a fresh session's skill listing — Claude side proven (this session lists the skill via the existing `~/.claude/skills/agent-resume-review` junction); the literal `distribute --scope user` run is currently blocked by 2 pre-existing conflicts in unrelated entries (see Progress log)

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/agent-resume-review/scripts/resume_lint.py (4 bundled samples, --json vs expected_outputs/) | 0 | 4/4 MATCH — weak 45.7 zh · strong 100.0 zh · weak-en 43.6 en · strong-en 100.0 en |
| python -m unittest discover .agents/skills/agent-resume-review/tests | 0 | 15 tests OK |
| python docs/dotagents/init_dotagents_folder.py validate | 0 | OK: 52 file(s) valid, 3 warning(s) — all pre-existing (empty models.json placeholder; 2 non-kebab agent names, CHANGE-003 §8.4 decision); no new warnings from this skill |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 0 | 7/7 skills PASS (min score 90); agent-resume-review quality 96.1 (A+); also enforced by the pre-commit hook at 2b3d2e1 |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 7/7 skills PASS (100%), 0 ERROR |

## Progress log

- 2026-10-14 — open: ticket created
- 2026-10-14 — open → in-progress; branch feature/CHANGE-004-agent-resume-review created; scope: land the pre-built skill (built and gate-passed 2026-10-13, quality 96.1) from the working tree — no new feature work, only verification + registration
- 2026-10-14 — skill (21 files) + registry entry committed (2b3d2e1); pre-commit skill gate PASS 96.1; full verification suite recorded above; distribution state: claude user+project links already in place (live session lists the skill), project-scope re-run added the missing `.github/skills/agent-resume-review` junction for copilot. Pre-existing, out-of-scope leftovers noted: 8 broken copilot links under `.github/*` (repo relocation) and 2 `~/.agents/skills` conflicts (agent-designer, agent-workflow-designer point elsewhere) that make `distribute --scope user` refuse — resolving them is a user decision, not this ticket's scope

## Acceptance record

(Verdict: accepted / rejected · date · notes)

## Release record

- Version: (pending)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
