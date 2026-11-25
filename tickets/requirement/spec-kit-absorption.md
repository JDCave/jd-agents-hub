# Requirement Analysis: Spec-Kit Skill Absorption

- **Date**: 2026-11-08
- **Status**: Draft (requirements analysis + working-tree implementation — no ticket opened)
- **Scope**: Absorb the reusable process skills from GitHub spec-kit into the hub's
  `.agents/` SSOT as three hub-native skills, so the existing distribution engine
  ships them to Claude Code, Codex, OpenCode, and Copilot.
- **Source**: local clone `D:\workspace\code\opensource\github\spec-kit`, commit
  `c43849408ac0de2ca6a52f14eaae71449776057b` (2026-11-06), `specify-cli
  1.3.3.dev0`, MIT (Copyright GitHub, Inc.). Read-only; nothing upstream was
  modified.

---

## 1. Background

spec-kit is GitHub's toolkit for spec-driven development. Its "skills" are the
command templates under `templates/commands/` (and `extensions/*/commands/`),
which its CLI renders into per-agent skill files such as
`.claude/skills/speckit-<command>/SKILL.md`, `.github/skills/...`,
`.agents/skills/...`. Users invoke them in the agent chat
(`/speckit-specify`, `$speckit-specify`, ...); the `specify` CLI is only the
installer/manager.

This hub already owns the delivery half of that equation: `.agents/skills/` is
the SSOT and `scripts/distribute.py` installs it into each agent's native
discovery location. So the absorption work is to port spec-kit's *process
content* into hub skills, not to adopt spec-kit's CLI.

## 2. Capability inventory (what spec-kit's skills do)

spec-kit frames three independent user processes, not one mandatory pipeline.

### 2.1 Core SDD — 9 command skills (`templates/commands/`)

Order (per upstream docs): `constitution → specify → clarify → plan →
checklist → tasks → analyze → implement → converge`. Only `specify` is strictly
required before `plan`; clarify, checklist, and analyze are optional gates.

| Step | Capability | Primary artifacts |
|---|---|---|
| constitution | Establish/amend project principles that every later phase is checked against; semver bump rules, MUST/SHOULD + rationale, TODO placeholders, sync impact report | `.specify/memory/constitution.md` |
| specify | Turn a natural-language request into WHAT/WHY spec: user stories with priorities, testable functional requirements, measurable technology-agnostic success criteria, key entities, assumptions; ≤ 3 `[NEEDS CLARIFICATION]`; requirements-quality checklist | `specs/NNN-name/spec.md`, `checklists/requirements.md`, `.specify/feature.json` |
| clarify | Resolve ambiguity before planning: up to 5 multiple-choice questions, answers written back into `spec.md`, checklist updated | edits `spec.md` |
| plan | Technical plan: Technical Context, Constitution Check gate, Phase 0 `research.md` (Decision/Rationale/Alternatives), Phase 1 `data-model.md`, `contracts/`, `quickstart.md`, post-design constitution re-check | `plan.md` + design artifacts |
| checklist | Requirements-quality review artifact owned by a reviewer — "unit tests for requirements writing"; never records implementation progress | `checklists/<domain>.md` |
| tasks | Dependency-ordered, immediately executable `tasks.md`: strict `- [ ] T001 [P] [US1] … file path` format, phases by user story, dependency graph, parallel examples, MVP scope; tests optional | `tasks.md` |
| analyze | Read-only cross-artifact consistency audit of spec/plan/tasks with CRITICAL/HIGH/MEDIUM/LOW findings, findings table, coverage metrics; never applies fixes | none (in-chat) |
| implement | Execute tasks phase by phase, respect dependencies, run the checklist gate and ask before proceeding, mark `[X]`, validate against spec/plan | source code, `tasks.md` |
| converge | Compare code to spec/plan/tasks, classify gaps (missing/partial/contradicts/unrequested), **append-only** `## Phase N: Convergence` block; byte-identical `tasks.md` when converged | `tasks.md` |

Cross-cutting mechanisms: constitution authority; the ≤3 NEEDS CLARIFICATION cap
(priority scope > security/privacy > UX > technical); checklist ownership;
analyze read-only + fixed severity ladder; converge append-only loop; extension
hooks registered in `.specify/extensions.yml`; optional agent-context updates.

### 2.2 Bug triage — 3 command skills (`extensions/bug/`)

`assess → fix → test`, one directory `.specify/bugs/<slug>/` with
`assessment.md`, `fix.md`, `test.md`. Assess and test never modify source; fix
is the only editing stage and logs deviations. Verification verdicts are
`verified` / `partial` / `failed` / `not-run` and are never over-claimed. URL
input follows a trust policy (allowlisted public sources, unknown hosts
prompt-or-skip, loopback/RFC1918/metadata endpoints refused, fetched content is
untrusted data).

### 2.3 Idea assessment — 5 command skills (`extensions/assess/`)

`intake → research → define → shape → decide`, one directory
`.specify/assessments/<slug>/` with `intake.md`, `research.md`, `problem.md`,
`concept.md`, `decision.md`. It is a funnel: most ideas should be killed or
parked before shape; `define` is the minimum viable stage; `shape` requires
`problem.md`; `decide` requires `problem.md` and a `go` without `concept.md`
downgrades to `needs-clarification`. Verdicts: `go` / `needs-clarification` /
`kill`; `go` hands its decision summary to the SDD process. Research always
includes an "Evidence Against the Idea" section and tags unsourced claims
`ASSUMPTION`.

### 2.4 Auxiliary commands and composition layers (deliberately not skills)

git extension (5 commands, 18 hooks), GitHub issue export (1), agent-context
updates (1), selftest (1); presets, bundles, workflow engine, catalogs,
integration dispatch and the `specify` CLI. These are platform glue for
spec-kit itself, not process capabilities a portable skill needs.

## 3. Hub constraints that shape the absorption

- The `.agents/` SSOT is distributed by `scripts/distribute.py`, one directory
  per skill; skill folders are linked as-is, so all paths must be relative.
- The repo's skill gate requires, per skill: `SKILL.md` ≤ 100 total lines,
  frontmatter `name` = folder name + a description with a "Use when" trigger,
  6/6 authoring checklist items, a stdlib `argparse` script with a main guard,
  flat `references/` (no nested markdown), quality score ≥ 90, security PASS,
  no built-in-name shadowing.
- Skills ship to four agents; each skill's description enters the agents'
  skill listings, so a small number of well-scoped skills is preferable to one
  skill per upstream command.
- Repository change lifecycle (branch/tag/PR) is already owned by
  `change-ticket-deliver`; spec-kit's git extension is therefore redundant.

## 4. Decision: three process skills

| New hub skill | Covers | Rationale |
|---|---|---|
| `spec-driven-development` | the 9 core commands | one user journey over one feature directory and one constitution; the cross-artifact gates (analyze, converge) only make sense together |
| `bugfix-triage` | the 3 bug commands | separate user intent ("a bug report arrived") and disjoint state (`.specify/bugs/`) |
| `idea-assessment` | the 5 assess commands | separate user intent ("should we build this?") and disjoint state (`.specify/assessments/`); upstream also frames it as an independent entry point |

Each `SKILL.md` is a thin router; per-command detail lives in flat
`references/command-<step>.md` (SDD) or `references/<stage>.md` (bug/assess),
loaded only for the step being run.

Rejected alternatives:

- **17 command-level skills** (spec-kit's own model): would duplicate the shared
  mechanisms 17 times, exceed the 100-line ceiling once mechanisms are included,
  crowd the agents' skill listings, and require 17 sets of scripts/tests for one
  deterministic workflow.
- **One umbrella skill**: loses trigger distinctness between "build a feature",
  "triage a bug", and "assess an idea", and hides the three independent entry
  points upstream documents.

## 5. Porting strategy (hybrid)

Port the **process**, not the platform:

- Keep the `.specify/` on-disk artifact contract
  (`memory/constitution.md`, `templates/`, `feature.json`, `specs/NNN-name/`,
  `.specify/bugs/<slug>/`, `.specify/assessments/<slug>/`) — the durable
  in-repo artifacts are the user-facing value.
- Rewrite command prose into references, keeping the hard gates, caps, IDs,
  artifact schemas and error conditions close to verbatim. Replace every
  spec-kit renderer token (`{SCRIPT}`, `__SPECKIT_COMMAND_*__`, `$ARGUMENTS`,
  hook blocks, `specify extension add`) with plain hub instructions and
  skill-relative script calls.
- Reimplement the mechanical parts as one compact stdlib script per skill
  instead of vendoring spec-kit's CLI helpers (which pull `subprocess`/YAML
  paths that the hub's script and security gates reject):
  - SDD: `scripts/sdd_workflow.py` — `bootstrap`, `new-feature` (sequential
    `NNN` allocation, slug derivation, `feature.json`), `prereqs`, `plan`,
    `tasks`, `status`, `resolve-template` (project override → bundled asset).
  - Bug: `scripts/bug_workflow.py` — slug normalization/uniqueness/path safety,
    report scaffolding, stage status, verdict validation.
  - Assess: `scripts/assess_workflow.py` — slug/path safety, stage
    scaffolding, funnel preconditions, verdict validation/downgrade.
- Drop the `specify` CLI, integrations, presets, extension hooks, catalogs,
  bundles, workflow engine, git/GitHub/agent-context/selftest extensions; the
  hub's change workflow owns branch/commit/PR. Branch creation is the only
  git-extension behavior referenced, and it stays out of the skills.
- Sequential feature numbering only; timestamp numbering is dropped.
- Attribution: each skill ships `references/upstream.md` with the source URL,
  commit pin, ported-file table, modification/drop lists, and the full MIT
  notice. Templates copied from spec-kit keep their upstream placeholder
  conventions; only renderer tokens were normalized (`__SPECKIT_COMMAND_X__` →
  "the X step", `$ARGUMENTS` → `[FEATURE DESCRIPTION]`).

## 6. Deliverables (working tree)

```
.agents/skills/spec-driven-development/   34 files: SKILL.md, README.md,
    references/ (9 command references + mechanisms + upstream),
    assets/templates/ (5 page templates) + 5 samples,
    scripts/sdd_workflow.py, expected_outputs/ (4), tests/ (32 cases)
.agents/skills/bugfix-triage/             21 files: SKILL.md, README.md,
    references/ (assess, fix, test, url-trust-policy, upstream),
    assets/ (3 report templates + 4 samples),
    scripts/bug_workflow.py, expected_outputs/ (4), tests/ (29 cases)
.agents/skills/idea-assessment/           23 files: SKILL.md, README.md,
    references/ (5 stage references + url-trust-policy + upstream),
    assets/ (5 stage templates + 3 samples),
    scripts/assess_workflow.py, expected_outputs/ (4), tests/ (27 cases)
.agents/skills/registry.json              +3 entries (draft, gate PASS)
README.md                                 +3 rows in the skills catalog
tickets/requirement/spec-kit-absorption.md  this analysis
```

The three skills are **not** `hub_only`: they depend only on their own bundled
assets and a `.specify/` directory they bootstrap in the target project, so
they distribute to every target and every scope.

## 7. Verification evidence

| Check | Command | Result |
|---|---|---|
| Gate, SDD | `python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/spec-driven-development --json` | PASS, 8/8 checks, quality **99.0** (Docs 96.9 · Code 98.0 · Complete 100 · Security 100 · Usability 100) |
| Gate, bugfix | same for `bugfix-triage` | PASS, 8/8, quality **98.3** (98.6 · 98.0 · 100 · 100 · 95.0) |
| Gate, assess | same for `idea-assessment` | PASS, 8/8, quality **97.9** (96.7 · 98.0 · 100 · 100 · 95.0) |
| Unit tests | `python -m unittest discover -s .agents/skills/<name>/tests` | 32 / 29 / 27 tests, all OK |
| CLI smoke | no args, `--help`, sample asset as positional target | exit 0 in all three skills |
| Repo-wide audit | `python .agents/skills/skill-tester/scripts/audit_skills.py` | 11/11 skills at 6/6 checklist items (100 %) |
| SSOT validate | `python docs/dotagents/init_dotagents_folder.py validate --root .` | OK: 71 files valid, 3 pre-existing warnings (empty `models.json`, 2 non-kebab agent names) |
| Full gate | `python .agents/skills/skill-tester/scripts/skill_gate.py --all` | 10/11 PASS; the only block is the pre-existing **untracked** `caveman` skill (quality 59.6), unrelated to this change |
| Distribution | `python scripts/distribute.py distribute --dry-run` | 17 new, 0 updated, 22 native, **0 conflicts**; the three skills would link into `.claude/skills/` and `.github/skills/` and are native for Codex/OpenCode |

## 8. Licensing

spec-kit is MIT. The ported material is limited to process prose, five page
templates, three bug report templates, five assessment stage templates, and the
documented script behavior. Every skill's `references/upstream.md` carries the
source, the pinned commit, the ported-file table, the list of modifications and
drops, and the full MIT copyright/permission notice. No spec-kit media or
logos are redistributed, and nothing implies GitHub endorsement.

## 9. Re-sync policy

Pin the commit (above) in each `references/upstream.md`; on a future upstream
release, diff the ported file list, re-read the command templates for gate
changes, re-run the three unit suites and the hub gate, and update the pin. The
five page templates and the command reference bodies are the most likely to
drift and should be diffed first.

## 10. Follow-ups (not done by this change)

- Record the change through the repo's change workflow (`change-ticket-deliver`)
  to get a ticket, semver tag, CHANGELOG entry, and PR.
- Run the real `python scripts/distribute.py distribute` (project and/or user
  scope) when the new skills should become visible in the local agent tools;
  the dry run above is conflict-free.
- Decide whether the ported skills should be promoted from registry `draft` to
  `review`/`published` after a review pass.
