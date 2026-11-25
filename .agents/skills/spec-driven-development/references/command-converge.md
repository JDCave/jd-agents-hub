# Converge — append remaining work as new tasks

Ported from spec-kit `templates/commands/converge.md` at commit
`c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Close the gap between what a feature's specification, plan, and tasks call for and
what the codebase currently implements. Read `spec.md`, `plan.md`, and `tasks.md`
as the **sole source of intent**, with the constitution as governing constraints.
Assess the current state of the code, determine which requirements, acceptance
criteria, plan decisions, and existing tasks are unmet, incomplete, or only
partially satisfied, and **append each piece of remaining work as a new, traceable
task** at the bottom of `tasks.md` so the implement step can complete it. Read this
file only when running the converge step.

This step MUST run only after the implement step has run on the current
`tasks.md`, and after the tasks step has produced a complete `tasks.md`.

This is **not** a diff utility and does **not** track changes. It assesses the
present state of the code relative to the feature's artifacts: no git, no branch
comparison, no history.

## Operating Constraints

**APPEND-ONLY, NEVER REWRITE**: the only write is appending a new
`## Phase N: Convergence` section to `tasks.md`. This step MUST NOT:

- modify `spec.md` or `plan.md` in any way;
- rewrite, renumber, reorder, or delete any existing task, including tasks from a
  prior Convergence phase;
- modify, create, or delete any application code; completing the appended tasks
  is the job of the implement step.

When the codebase already satisfies everything, the step MUST leave `tasks.md`
**byte-for-byte unchanged** (no empty Convergence header) and report a clean
result.

**Constitution authority**: the project constitution is **non-negotiable**. Code
that violates a MUST principle is the highest-severity finding and produces a
corresponding remediation task. When the constitution is an unfilled template, skip
constitution checks gracefully rather than failing.

## Execution Steps

### 1. Initialize the convergence context

```bash
python scripts/sdd_workflow.py --action prereqs --require-spec --require-tasks --json
```

Parse `FEATURE_DIR` and `AVAILABLE_DOCS` once. Derive absolute paths:

- SPEC = `<FEATURE_DIR>/spec.md`
- PLAN = `<FEATURE_DIR>/plan.md`
- TASKS = `<FEATURE_DIR>/tasks.md`
- CONSTITUTION = `.specify/memory/constitution.md` when present.

If `spec.md`, `plan.md`, or `tasks.md` is missing, STOP with a clear, actionable
message naming the prerequisite step to run: specify for a missing spec, plan for a
missing plan, tasks for missing tasks. Do not produce partial output.

### 2. Load artifacts (progressive disclosure)

Load only the minimal necessary context from each artifact.

**From `spec.md`**:
- Functional Requirements (FR-###).
- Success Criteria (SC-###); include only items requiring buildable work and
  exclude post-launch outcome metrics and business KPIs.
- User Stories and their Acceptance Scenarios.
- Edge Cases when present.

**From `plan.md`**:
- Architecture and stack choices, plus technical decisions.
- Data-model references.
- Phases and named touch-points (files and components the plan says will be
  created or edited).
- Technical constraints.

**From `tasks.md`**:
- Task ids, to compute the next id and the next phase number.
- Descriptions, phase grouping, and referenced file paths.

**From the constitution** when it is not an unfilled template:
- Principle names and MUST or SHOULD normative statements.

### 3. Build the intent inventory

Create an internal model and do not echo raw artifacts:

- **Requirements inventory**: one stable key per FR-###, SC-###, or user-story
  acceptance scenario (for example `US1/AC2`), plus the plan decisions and
  constitution principles that impose buildable obligations.
- **Code-scope map**: from the file paths named in `plan.md` and `tasks.md`, plus a
  keyword search for the concepts each requirement describes, derive the set of
  source files and components in scope for assessment. Bound the assessment to
  these files; do not infer scope beyond what the artifacts define.

### 4. Assess the codebase and classify findings

Include every existing task in the intent inventory, regardless of checkbox state
or Convergence phase: completion claims are not evidence. Verify current behavior
against the spec, plan, tasks, and constitution. For corrective task chains,
assess the resulting behavior, not superseded implementation details. Check both
unmet obligations and implementation that contradicts, exceeds, or falls outside
the stated intent.

For each item in the intent inventory, inspect the current code in scope and
produce a finding only where there is a gap. Classify every finding by **gap
type**:

- **`missing`**: the required work is absent from the code entirely.
- **`partial`**: the work exists but does not yet fully satisfy the requirement,
  acceptance criterion, or plan decision.
- **`contradicts`**: the code does something that conflicts with stated intent or
  a constitution MUST principle.
- **`unrequested`**: the code contains work not called for by the spec, plan, or
  tasks. Surface it for awareness; converge does not delete code, it only appends
  a task to review, justify, or remove it.

Each finding records a stable id, the `source-ref` it traces to, the `gap-type`, a
severity, and a short human-readable description with the evidence (the file or
area observed).

**Edge cases**:

- **Little or no code yet**: treat the entire specified scope as `missing`
  remaining work rather than failing.
- **Nothing remains**: produce zero findings and follow the converged branch in
  step 7.

### 5. Assign severity

- **CRITICAL**: violates a constitution MUST principle, or a `missing` or
  `contradicts` gap that blocks baseline functionality of a P1 user story.
- **HIGH**: a `missing` or `partial` gap on a core functional requirement or
  acceptance criterion.
- **MEDIUM**: a `partial` gap on a secondary requirement, or an `unrequested`
  addition with unclear justification.
- **LOW**: minor partial gaps, polish, or low-risk `unrequested` additions.

### 6. Present the in-session findings summary

Before appending anything, output a compact, severity-graded summary with no file
writes yet:

```markdown
## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
| F1 | missing  | HIGH     | FR-008 | Example: no append-only guard detected in path/to/module.py when writing tasks.md | Add append-only enforcement |
```

**Summary metrics**:
- Requirements and acceptance criteria checked.
- Plan decisions checked.
- Constitution principles checked, or "skipped, template".
- Findings by gap type (missing, partial, contradicts, unrequested).
- Findings by severity.

### 7. Append convergence tasks, or report converged

**When there are one or more actionable findings** (the `tasks_appended` outcome):

Append to the **end** of `tasks.md`, following the append contract:

1. Scan all existing task ids; let `M` be the maximum. Determine the next phase
   number `N` as the highest existing phase plus 1.
2. Write a single new section header `## Phase N: Convergence`.
3. Emit one checklist item per actionable finding, ordered CRITICAL and HIGH
   first, assigning zero-padded ids `T{M+1:03d}`, `T{M+2:03d}`, and so on:

   ```markdown
   - [ ] T042 <imperative description> per <source-ref> (<gap-type>)
   ```

   `<source-ref>` traces the task to its origin, for example `FR-003`, `SC-002`,
   `US1/AC2`, `plan: storage decision`, or `Constitution II`.

   `<gap-type>` is one of `missing`, `partial`, `contradicts`, or `unrequested`.

   Constitution-violation tasks MUST be emitted first and described as `CRITICAL`.
4. Never reuse or renumber existing ids. When a prior Convergence phase exists, add
   a new, separately numbered one below it; do not touch the old one.

**When there are no actionable findings** (the `converged` outcome):

- Do **not** modify `tasks.md` at all; no empty phase header.
- Report: **"Converged: the implementation satisfies the spec, plan, and tasks."**
- Include the summary counts of what was checked.

### 8. Provide next actions (handoff)

- On `tasks_appended`: state how many tasks were appended under which phase, and
  recommend running the implement step to complete them; note that a follow-up
  converge run will find fewer or no remaining items.
- On `converged`: recommend proceeding to review or opening a pull request. No
  further implement pass is needed for this feature's specified scope.

## Done When

- [ ] Findings summary emitted in-session before any write
- [ ] Append contract followed exactly when tasks were appended, or `tasks.md`
      left byte-for-byte unchanged when converged
- [ ] No existing task renumbered, reordered, or deleted
- [ ] Outcome (`tasks_appended` or `converged`) reported with next actions

Next step: on `tasks_appended`, run the implement step again
([command-implement.md](command-implement.md)); on `converged`, proceed to review
or delivery.

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
