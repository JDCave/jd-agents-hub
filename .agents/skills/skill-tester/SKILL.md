---
name: "skill-tester"
version: "2.1.0"
license: "MIT"
when_to_use: "When the skill gate fails and you need the underlying detail; when auditing a skill's tier; when extending the scoring rubric."
description: "Validate, test, and score the quality of skills within the claude-skills ecosystem. Comprehensive meta-skill: structure validation, Python script testing (syntax + imports + runtime + output format), multi-dimensional quality scoring with letter grades and tier classification (BASIC/STANDARD/POWERFUL). Use when authoring a new skill, auditing existing skills for tier promotion, setting up pre-commit hooks for skill quality, or integrating skill QA into CI."
---

# Skill Tester

**Tier**: POWERFUL · **Category**: Engineering Quality Assurance · **Dependencies**: None (Python stdlib only)

Meta-skill that validates, tests, and scores skills in this repository. Four tools, run from the **repo root** with full paths:

1. **`scripts/skill_validator.py`** — structure + documentation compliance
2. **`scripts/script_tester.py`** — Python script syntax/imports/runtime/output testing
3. **`scripts/quality_scorer.py`** — multi-dimensional scoring with letter grade
4. **`scripts/security_scorer.py`** — security posture scoring (also available via `quality_scorer.py --include-security`)

> **Scope note:** this skill's tier line-count minimums measure *legacy* skills. For authoring *new* skills, `skill-builder` (SKILL.md under ~100 lines, Matt Pocock doctrine) is the binding standard — do not pad a new skill to satisfy a tier minimum here.

## Quick Start (exact, runnable from repo root)

```bash
# 1. Validate structure (exit non-zero on failure — usable as a gate)
python .agents/skills/skill-tester/scripts/skill_validator.py .agents/skills/skill-builder --json

# 2. Test the skill's Python scripts (30s default timeout per script)
python .agents/skills/skill-tester/scripts/script_tester.py .agents/skills/skill-builder --json

# 3. Score quality (fail CI below threshold with --minimum-score)
python .agents/skills/skill-tester/scripts/quality_scorer.py .agents/skills/skill-builder --json --detailed --minimum-score 90
```

Consume the JSON: validator emits `overall_score`, `compliance_level`, per-check `checks{}`; scorer emits `overall_score`, `letter_grade`, `tier_recommendation`, `dimensions`, and an `improvement_roadmap` — work the roadmap top-down, then re-run until the target score is met.

For one-command gating of a skill (frontmatter + names + checklist + all tools above + security audit, single exit code), use the repo-root gate:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>    # one skill, min score 90
python .agents/skills/skill-tester/scripts/skill_gate.py --all                   # every skill
```

For repo-wide auditing prefer `.agents/skills/skill-tester/scripts/audit_skills.py` (wraps the skill-builder checklist runner across all skills).

## What Each Script Checks

### skill_validator.py
- SKILL.md frontmatter parsing, required sections, minimum line counts per tier (`--tier BASIC|STANDARD|POWERFUL`)
- Required structure: SKILL.md, README.md, scripts/, references/, assets/, expected_outputs/
- Python scripts: argparse present, stdlib-only imports

### script_tester.py
- AST-based syntax validation; import analysis (flags external dependencies)
- Controlled execution with timeout protection (`--timeout`, default 30s)
- `--help` functionality verification; sample-data runs compared against expected_outputs/

### quality_scorer.py
Four dimensions, 25% each: **Documentation** (depth, examples, references), **Code Quality** (complexity, error handling, output consistency), **Completeness** (required dirs, sample data, expected outputs), **Usability** (help text, example clarity). Outputs 0-100 + A-F grade + tier recommendation.

## Tier Classification

| Tier | SKILL.md | Scripts | CLI surface |
|---|---|---|---|
| BASIC | ≥ 100 lines | 1 (100-300 LOC) | basic argparse |
| STANDARD | ≥ 200 lines | 1-2 (300-500 LOC) | subcommands, JSON + text output |
| POWERFUL | ≥ 300 lines | 2-3 (500-800 LOC) | multiple modes, CI integration |

(Advisory for legacy skills; new skills follow skill-builder — see scope note above.)

## CI Integration

```yaml
# GitHub Actions: gate changed skills
- name: "gate-skills"
  run: python .agents/skills/skill-tester/scripts/skill_gate.py --all --update-registry   # min score 90, security FAIL blocks
```

Pre-commit hook: `.githooks/pre-commit` (install once with `git config core.hooksPath .githooks`) runs the skill gate on each staged skill directory and blocks the commit on non-zero exit.

## Verification Loop

A skill "passes" when, in one run from repo root:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>
```

exits 0 (this runs validator + script tester + quality scorer ≥ 90 + security audit + frontmatter/name checks).

If the gate fails, apply the top `improvement_roadmap` item (in the `quality` check's JSON detail) and re-run the gate — never report a partial pass.

## Troubleshooting

- **Timeout errors** → raise `--timeout` or optimize the script under test
- **Import failures** → external deps detected; stdlib-only is the repo policy
- **Tier misclassification** → check line counts/LOC against the tier table; remember the skill-builder exception for new skills

References: `references/` holds the structure specification, tier requirements matrix, and scoring rubric the tools implement.
