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

- [ ] Skill committed under `.agents/skills/agent-resume-review/` (SKILL.md, scripts, tests, references, assets, expected_outputs, README, examples) — no build artifacts (`__pycache__` stays ignored)
- [ ] `registry.json` carries the `agent-resume-review` entry with its latest gate result
- [ ] Lint demo run exits 0; lint reproduces `expected_outputs/` scores for the four bundled samples (zh/en × strong/weak)
- [ ] `python -m unittest discover .agents/skills/agent-resume-review/tests` passes
- [ ] `init_dotagents_folder.py validate` clean for the new skill (kebab-case name matches directory, required frontmatter present)
- [ ] skill gate PASS (quality ≥90) for all skills and repo-wide audit has no ERROR
- [ ] Manual: after `distribute --scope user`, the skill appears in a fresh session's skill listing

## Verification evidence

| Command | Exit code | Result |
| --- | --- | --- |
| python .agents/skills/agent-resume-review/scripts/resume_lint.py |  |  |
| python -m unittest discover .agents/skills/agent-resume-review/tests |  |  |
| python docs/dotagents/init_dotagents_folder.py validate |  |  |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all |  |  |
| python .agents/skills/skill-tester/scripts/audit_skills.py |  |  |

## Progress log

- 2026-10-14 — open: ticket created
- 2026-10-14 — open → in-progress; branch feature/CHANGE-004-agent-resume-review created; scope: land the pre-built skill (built and gate-passed 2026-10-13, quality 96.1) from the working tree — no new feature work, only verification + registration

## Acceptance record

(Verdict: accepted / rejected · date · notes)

## Release record

- Version: (pending)
- Tag: (pending)
- PR: (pending)
- Merged: (pending)
