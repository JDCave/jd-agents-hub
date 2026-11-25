---
name: spec-driven-development
version: "1.0.0"
license: MIT
description: "Run a spec-driven development workflow that keeps a durable constitution, feature specification, technical plan, and task list in `.specify/`, then implements and converges against them instead of re-deriving intent from chat. Use when starting a feature from a natural-language request, planning and breaking work into tasks, checking spec-plan-task consistency before implementation, or closing gaps between the artifacts and the delivered code."
when_to_use: "Starting a new feature or turning a feature request into spec, plan, and tasks; running a consistency check before implementation; converging after implementation."
---

# Spec-Driven Development

Turn a feature request into durable in-repo artifacts — constitution, spec, plan, tasks — and make implementation check those artifacts instead of chat memory. Read `references/command-<name>.md` only for the step being run; the nine step files are flat under `references/`.

## Quick Start

```bash
python scripts/sdd_workflow.py --action bootstrap --json
python scripts/sdd_workflow.py --action new-feature --title "add user authentication" --json
python scripts/sdd_workflow.py --action prereqs --json
```

## When to Use

- A feature request must become a specification, a technical plan, and an executable task list
- Implementation must be checked against a spec and plan instead of memory

## Workflows

Run the steps in this order; clarify, checklist, and analyze are optional quality gates:

1. **constitution** — establish or amend `.specify/memory/constitution.md`
2. **specify** — feature spec with user stories, requirements, and success criteria
3. **clarify** (optional) — resolve ambiguity before planning
4. **plan** — Technical Context, Constitution Check, research, data model, contracts, quickstart
5. **checklist** (optional) — requirements-quality review artifact
6. **tasks** — ordered `tasks.md` grouped by user story
7. **analyze** (optional) — read-only cross-artifact consistency audit
8. **implement** — execute tasks phase by phase and mark them `[X]`
9. **converge** — append remaining work, or confirm the feature converged

## Cross-cutting Rules

1. **Constitution authority**: `.specify/memory/constitution.md` wins; plan reports an ERROR for an unjustified violation, analyze marks a conflict CRITICAL, converge ranks it first.
2. **Max 3 `[NEEDS CLARIFICATION]` markers** in the spec, priority scope > security/privacy > UX > technical; clarify asks at most 5 questions and writes answers back into `spec.md`.
3. **Checklist ownership**: `checklists/requirements.md` belongs to specify and clarify; custom checklists are reviewer-owned requirements-quality review artifacts and never record implementation progress.
4. **Analyze is read-only**: it writes nothing and labels every finding CRITICAL, HIGH, MEDIUM, or LOW.
5. **Converge is append-only**: its only write is a `## Phase N: Convergence` block in `tasks.md`; when everything is satisfied, `tasks.md` stays byte-identical.

## Artifact Map

```text
.specify/memory/constitution.md    principles and governance
.specify/feature.json              {"feature_directory": "specs/NNN-name"}
specs/NNN-name/{spec,plan,tasks}.md   specification, technical plan, ordered tasks
specs/NNN-name/{research,data-model,quickstart}.md   Phase 0/1 design artifacts
specs/NNN-name/{contracts,checklists}/   Phase 1 interfaces and requirements checklists
```

The artifacts hold the API contracts, architecture notes, algorithm choices, implementation detail level, performance targets, scalability limits, security constraints, integration boundaries, configuration values, and parameters that later steps read.

## Output Format

```json
{"FEATURE_DIR": "specs/001-add-user-authentication", "SPEC_FILE": "specs/001-add-user-authentication/spec.md", "FEATURE_NUM": "001"}
```

Usage: pass `--json` for one stable JSON object per action; without it every action prints one line per item. Exit 0 is success, 2 is bad input or a missing prerequisite.

## Verification

```bash
python -m unittest discover -s tests
python scripts/sdd_workflow.py --help; python scripts/sdd_workflow.py assets/sample-feature.json
```

Verify and test the artifacts against the spec too: a passing unit suite proves the script, not the feature.

## References

- Step files: [constitution](references/command-constitution.md), [specify](references/command-specify.md), [clarify](references/command-clarify.md), [plan](references/command-plan.md), [checklist](references/command-checklist.md), [tasks](references/command-tasks.md), [analyze](references/command-analyze.md), [implement](references/command-implement.md), [converge](references/command-converge.md)
- [mechanisms.md](references/mechanisms.md) — cross-cutting rules, artifact contract, script contract; [upstream.md](references/upstream.md) — provenance, attribution, and the drop list

## Troubleshooting

| Symptom | Fix |
|---|---|
| `already exists (pass --force)` | inspect the file, then pass `--force` only when a replacement is intended |

Example: `python scripts/sdd_workflow.py --action status --json` summarizes the workspace and always exits 0.

## Limitations

- The `specify` CLI, integration dispatch, presets, and extension hooks are deliberately not ported
- Branch, commit, and pull-request lifecycle belongs to the hub's change workflow
- A validation loop cannot invent intent that the spec, plan, and tasks never recorded
