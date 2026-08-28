# Skill Lifecycle Management

This document describes how skills in this repository move through their
lifecycle — from creation, through evaluation and gating, to optimization —
and how the bundled skills and scripts enforce that lifecycle automatically.

## Overview

The lifecycle is a loop, not a pipeline:

```
 create/modify          evaluate                enforce                 optimize
┌──────────────┐   ┌──────────────────┐   ┌────────────────┐   ┌─────────────────┐
│ skill-builder │ → │ skill-tester/    │ → │ pre-commit hook │ → │ apply top       │
│ (authoring    │   │ skill_gate.py    │   │ + CI workflow   │   │ improvement_    │
│  doctrine)    │   │ (8 checks, one   │   │ (score < 90 or  │   │ roadmap item,   │
│               │   │  exit code)      │   │ security FAIL   │   │ re-run gate     │
└──────────────┘   └──────────────────┘   │  blocks merge)  │   │ until PASS)     │
                                          └────────────────┘   └─────────────────┘
                                                        ↑                              │
                                                        └──────────────────────────────┘
```

A skill that scores below the threshold **cannot be committed** (pre-commit)
or **merged** (CI). There is no bypass short of `git commit --no-verify`,
which CI still catches.

## Components

**Boundary rule**: `.agents/` is self-contained. Every lifecycle capability
(gate, checkers, auditor, aggregate audit) lives inside the skill that owns
it, and all internal paths resolve relative to each script's own location.
Nothing inside `.agents/` references the repo root `scripts/` directory.
Dependencies point one way only: repo-level facilities (`.githooks/`,
`.github/workflows/`) call into `.agents/`, never the reverse.

| Component | Location | Role in the lifecycle |
|---|---|---|
| `skill-builder` | `.agents/skills/skill-builder/` | **Create**: authoring doctrine (3-phase workflow, description rules, <100-line SKILL.md, progressive disclosure) + 3 validators |
| `skill-tester` | `.agents/skills/skill-tester/` | **Evaluate**: structure validation, script testing (syntax/imports/runtime/output), multi-dimensional quality scoring (0-100 + letter grade + improvement roadmap) |
| `skill-security-auditor` | `.agents/skills/skill-security-auditor/` | **Evaluate**: security scan (code execution risks, prompt injection, supply chain, file boundaries) → PASS/WARN/FAIL |
| `skill-lifecycle-orchestrator` | `.agents/agents/skill-lifecycle-orchestrator/agent.md` | **Orchestrate**: consistency persona; gates changed skills, walks the roadmap, same standard every time |
| `skill_gate.py` | `.agents/skills/skill-tester/scripts/` | **Enforce**: single entry point chaining all checks; all thresholds live here |
| `check_frontmatter.py` | `.agents/skills/skill-builder/scripts/` | Frontmatter validity (what Claude Code actually parses) |
| `check_skill_names.py` | `.agents/skills/skill-builder/scripts/` | Skill names must not shadow built-in slash commands |
| `audit_skills.py` | `.agents/skills/skill-tester/scripts/` | Repo-wide aggregate report (6-item checklist across all skills) |
| `registry.json` | `.agents/skills/registry.json` | Lifecycle state per skill (status + last gate result) |
| `.githooks/pre-commit` | `.githooks/pre-commit` | Fast local gate on staged skills |
| `skill-gate.yml` | `.github/workflows/skill-gate.yml` | Authoritative merge gate |

## The Gate

`.agents/skills/skill-tester/scripts/skill_gate.py` is the only enforcement entry point. Pre-commit and
CI call it; nothing calls the individual checkers directly. This keeps every
threshold in one file.

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>   # one skill
python .agents/skills/skill-tester/scripts/skill_gate.py --all                  # every skill
python .agents/skills/skill-tester/scripts/skill_gate.py --all --json           # machine-readable
python .agents/skills/skill-tester/scripts/skill_gate.py --all --update-registry  # record results in registry.json
```

### Checks (8 per skill)

| # | Check | Tool | Blocking condition |
|---|---|---|---|
| 1 | Frontmatter | `check_frontmatter.py` | any error (invalid YAML, missing description) |
| 2 | Name shadow | `check_skill_names.py` | skill name equals a built-in command |
| 3 | Checklist (6 items) | skill-builder checklist runner | any of the 6 items fails |
| 4 | Structure | skill-tester `skill_validator.py` | any error; SKILL.md > 100 lines is an error |
| 5 | Scripts | skill-tester `script_tester.py` | overall status FAIL |
| 6 | Quality | skill-tester `quality_scorer.py` | score < **90** |
| 7 | Security | skill-security-auditor | verdict FAIL (WARN records but does not block) |
| 8 | Naming | `skill_gate.py` `check_naming_convention` | folder name ≠ frontmatter name, or malformed name |

### Naming Convention

Meta-skills (skills that manage the skill lifecycle itself) are named
`skill-<role>` and cluster under the `skill-` prefix:

| Skill | Lifecycle role |
|---|---|
| `skill-builder` | create (authoring doctrine + validators; derived from Matt Pocock's upstream `write-a-skill`, MIT) |
| `skill-tester` | evaluate — quality |
| `skill-security-auditor` | evaluate — security |

The gate enforces that the folder name matches the frontmatter `name:`.
Task skills (non-meta, e.g. `pdf-extract`) don't carry the prefix — the
prefix is what makes the meta-family distinguishable in skill listings.

### Thresholds (centralized in `skill_gate.py`)

| Threshold | Value | Rationale |
|---|---|---|
| `MIN_SCORE` | **90** | letter grade A−/A territory; below this the skill is not publishable |
| `STRUCTURE_MIN` | 60 | skill_validator's own floor, re-checked centrally |
| Security FAIL | blocks | any CRITICAL finding |
| Security WARN | records | HIGH findings need human sign-off, not auto-block |

Exit codes: `0` = pass, `1` = blocked, `2` = usage/internal error.

## Enforcement Points

### 1. Pre-commit (local, fast)

```bash
git config core.hooksPath .githooks   # once per clone
```

`.githooks/pre-commit` detects staged changes under `.agents/skills/`, runs
the gate on each affected skill directory only, and blocks the commit on
non-zero exit. Bypassable with `--no-verify` — which is fine, because:

### 2. CI (authoritative)

`.github/workflows/skill-gate.yml` runs on every PR touching skills:

1. `skill_gate.py --all` (min score 90; any FAIL fails the job)
2. `audit_skills.py` (repo-wide aggregate report)
3. Uploads the JSON gate report as an artifact

CI is the real merge gate. A `--no-verify` local commit still fails the PR.

### 3. Registry (state)

`.agents/skills/registry.json` records per skill:

```json
{
  "skill-tester": {
    "status": "draft",
    "last_gate": {
      "timestamp": "2026-08-28T09:00:34+00:00",
      "verdict": "PASS",
      "quality_score": 90.3
    }
  }
}
```

Statuses: `draft` → `review` → `published` → `deprecated`. The gate updates
`last_gate` automatically (via `--update-registry`); status transitions are
human decisions:

- **draft → review**: author runs the gate locally until PASS
- **review → published**: PR merges with a green CI gate
- **→ deprecated**: skill kept for reference; excluded from promotion

## The Optimize Loop

When the gate blocks, it tells you exactly what to do:

```bash
$ python .agents/skills/skill-tester/scripts/skill_gate.py --all --json | python -c "
import json, sys
d = json.load(sys.stdin)
for r in d['results']:
    if r['verdict'] != 'PASS':
        print(r['skill'], r['checks']['quality']['detail']['improvement_roadmap'][:1])
"
```

Loop until green:

1. Read the failing checks and the top `improvement_roadmap` item
   (prioritized by dimension score impact).
2. Apply the fix (add the missing README section, split an over-long
   SKILL.md into references/, add error handling, etc.).
3. Re-run `python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>`.
4. Repeat. Never report a partial pass.

The scoring rubric is calibrated to the skill-builder doctrine: SKILL.md
under 100 lines scores *full marks* (not penalized for brevity), scripts are
scored on structural substance rather than raw LOC, and security tooling that
contains its own detection patterns is handled via the
`# noqa: SEC-AUDITOR` suppression convention rather than false positives.

## The Lifecycle Orchestrator (agent)

`.agents/agents/skill-lifecycle-orchestrator/agent.md` is a sub-agent persona
that applies this standard identically to every skill change — no reviewer
drift across sessions or authors.

- **Delegate to it** for batch work: "review the changed skills", "fix every
  FAIL skill to 90". It gates, interprets the JSON, walks the roadmap, and
  reports in one fixed format.
- **It enforces, it doesn't decide**: 89.x is FAIL, no rounding; registry
  `status` transitions stay human; security WARN sign-offs escalate.
- **Its scope is review-and-fix**: interactive creation (skill-builder's
  3-phase workflow needs the main conversation) and CI enforcement
  (pre-commit hooks, workflows — agents are not in that path) stay outside
  it. Single-stage tasks still route directly to `skill-builder` /
  `skill-tester` / `skill-security-auditor` via their trigger descriptions.

It orchestrates the same scripts the gate uses — the enforcement
guarantees (pre-commit, CI) never depend on any agent.

## Calibration Decisions (why the rubric looks like this)

The scoring tools were borrowed from an external repo whose rubric rewarded
behavior this repo's doctrine forbids. Key recalibrations made:

| Original rubric | Recalibrated | Why |
|---|---|---|
| SKILL.md length: 400+ lines = full marks | 30–100 lines = full marks | Doctrine: progressive disclosure; padding is an anti-pattern |
| Script complexity: 500+ LOC = full marks | structural substance (functions/docstrings/entry point) | A 40-line script doing one thing well is a good script |
| Frontmatter fields: `Name/Tier/Category/...` | `name/description` (+ optional) | The capitalized list matched no real skill; Claude Code reads lowercase YAML |
| Tier minimums: ≥100/200/300 lines | ceilings (max 100), advisory script sizes | Same anti-padding rationale |
| Library modules needed argparse + main guard | modules imported by siblings are exempt | `security_scorer.py` is a library, not a CLI |
| try/except-import counted as external dep | optional imports exempt | Graceful-degradation imports aren't dependencies |
| Security tool scanning its own patterns | noqa convention + comment stripping | The scanner's pattern table is not a vulnerability |

## Adding a New Skill (walkthrough)

```bash
# 1. Author with the doctrine (or ask the agent to use skill-builder)
mkdir -p .agents/skills/my-skill/{scripts,references,assets,expected_outputs}
# ... write SKILL.md (frontmatter + Quick start + Workflows, under 100 lines)

# 2. Gate it
python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/my-skill --update-registry

# 3. Walk the improvement_roadmap until PASS (score >= 90)

# 4. Commit — the pre-commit hook re-runs the gate automatically
git add .agents/skills/my-skill
git commit -m "Add my-skill"

# 5. PR — CI runs the full gate + repo-wide audit
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Gate fails "Description includes triggers" | Second sentence of `description:` must be `Use when [specific triggers]` |
| Gate fails "SKILL.md under 100 lines" | Move detail to `references/`; keep SKILL.md as the index |
| Gate fails "Consistent terminology" | Don't mix synonym pairs (skill/tool, agent/bot, user/developer) in one SKILL.md |
| Security flags a detection tool's own patterns | Append `# noqa: SEC-AUDITOR` to that line |
| `check_frontmatter.py needs PyYAML` | `pip install pyyaml` (CI installs it automatically) |
| Hook not running | `git config core.hooksPath .githooks` (once per clone) |
