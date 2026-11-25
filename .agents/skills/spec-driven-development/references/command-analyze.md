# Analyze — read-only cross-artifact consistency audit

Ported from spec-kit `templates/commands/analyze.md` at commit
`c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Identify inconsistencies, duplications, ambiguities, and underspecified items
across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before
implementation. Read this file only when running the analyze step. This step MUST
run only after the tasks step has produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: do NOT modify any file. Output a structured analysis
report. Offer an optional remediation plan; the user must explicitly approve before
any follow-up editing step runs manually.

**Constitution authority**: the project constitution
(`.specify/memory/constitution.md`) is **non-negotiable** within this analysis
scope. Constitution conflicts are automatically CRITICAL and require adjustment of
the spec, plan, or tasks, never dilution, reinterpretation, or silent ignoring of
the principle. If a principle itself needs to change, that must happen in a
separate, explicit constitution update outside this step.

## Execution Steps

### 1. Initialize the analysis context

```bash
python scripts/sdd_workflow.py --action prereqs --require-spec --require-tasks --json
```

Parse `FEATURE_DIR` and `AVAILABLE_DOCS` once. Derive absolute paths:

- SPEC = `<FEATURE_DIR>/spec.md`
- PLAN = `<FEATURE_DIR>/plan.md`
- TASKS = `<FEATURE_DIR>/tasks.md`

Abort with an error message when a required file is missing, instructing the user
to run the missing prerequisite step: specify for a missing spec, plan for a
missing plan, tasks for missing tasks.

### 2. Load artifacts (progressive disclosure)

Load only the minimal necessary context from each artifact.

**From `spec.md`**:
- Overview and context.
- Functional Requirements.
- Success Criteria (measurable outcomes: performance, security, availability,
  user success, business impact).
- User Stories.
- Edge Cases when present.

**From `plan.md`**:
- Architecture and stack choices.
- Data-model references.
- Phases.
- Technical constraints.

**From `tasks.md`**:
- Task ids.
- Descriptions.
- Phase grouping.
- Parallel markers [P].
- Referenced file paths.

**From the constitution**:
- Load `.specify/memory/constitution.md` for principle validation.

### 3. Build semantic models

Create internal representations and do not include raw artifacts in the output:

- **Requirements inventory**: for each Functional Requirement (FR-###) and Success
  Criterion (SC-###), record a stable key. Use the explicit FR- or SC- identifier
  as the primary key when present, and optionally derive an imperative-phrase slug
  for readability (for example "User can upload file" becomes
  `user-can-upload-file`). Include only Success Criteria that require buildable
  work (load-testing infrastructure, security audit tooling) and exclude
  post-launch outcome metrics and business KPIs such as "Reduce support tickets by
  50 percent".
- **User story and action inventory**: discrete user actions with acceptance
  criteria.
- **Task coverage mapping**: map each task to one or more requirements or stories,
  by inference from keywords or explicit reference patterns.
- **Constitution rule set**: extract principle names and MUST or SHOULD normative
  statements.

### 4. Detection passes (token-efficient analysis)

Focus on high-signal findings. Limit to 50 findings total and aggregate the
remainder in an overflow summary.

#### A. Duplication detection
- Identify near-duplicate requirements.
- Mark lower-quality phrasing for consolidation.

#### B. Ambiguity detection
- Flag vague adjectives (fast, scalable, secure, intuitive, robust) that lack
  measurable criteria.
- Flag unresolved placeholders (TODO, TKTK, question marks, angle-bracket
  placeholders).

#### C. Underspecification
- Requirements with verbs but a missing object or measurable outcome.
- User stories missing acceptance-criteria alignment.
- Tasks referencing files or components not defined in the spec or plan.

#### D. Constitution alignment
- Any requirement or plan element conflicting with a MUST principle.
- Missing mandated sections or quality gates from the constitution.

#### E. Coverage gaps
- Requirements with zero associated tasks.
- Tasks with no mapped requirement or story.
- Success Criteria requiring buildable work (performance, security, availability)
  that are not reflected in tasks.

#### F. Inconsistency
- Terminology drift (the same concept named differently across files).
- Data entities referenced in the plan but absent in the spec, or the reverse.
- Task ordering contradictions, for example integration tasks before foundational
  setup tasks without a dependency note.
- Conflicting requirements, for example one requires one framework while another
  names a different one.

### 5. Severity assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: violates a constitution MUST, missing core spec artifact, or a
  requirement with zero coverage that blocks baseline functionality.
- **HIGH**: duplicate or conflicting requirement, ambiguous security or
  performance attribute, untestable acceptance criterion.
- **MEDIUM**: terminology drift, missing non-functional task coverage,
  underspecified edge case.
- **LOW**: style or wording improvements, minor redundancy not affecting execution
  order.

### 6. Produce a compact analysis report

Output a Markdown report and write no files:

```markdown
## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |
```

Add one row per finding and generate stable ids prefixed by the category initial.

**Coverage summary table**:

```markdown
| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
```

**Constitution alignment issues**: list when any exist.

**Unmapped tasks**: list when any exist.

**Metrics**:
- Total requirements.
- Total tasks.
- Coverage percentage (requirements with at least one task).
- Ambiguity count.
- Duplication count.
- Critical-issue count.

### 7. Provide next actions

At the end of the report, output a concise Next Actions block:

- If CRITICAL issues exist, recommend resolving them before the implement step.
- If only LOW or MEDIUM issues exist, the user may proceed, but provide
  improvement suggestions.
- Provide explicit step suggestions: "Run the specify step with refinement", "Run
  the plan step to adjust architecture", or "Manually edit tasks.md to add
  coverage for performance metrics".

### 8. Offer remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top
N issues?" Do NOT apply them automatically.

## Operating Principles

### Context efficiency
- Focus on actionable findings, not exhaustive documentation.
- Load artifacts incrementally; do not dump all content into the analysis.
- Limit the findings table to 50 rows and summarize the overflow.
- Deterministic results: rerunning without changes should produce consistent ids
  and counts.

### Analysis discipline
- NEVER modify files; this is read-only analysis.
- NEVER invent missing sections; report them accurately when absent.
- Prioritize constitution violations; they are always CRITICAL.
- Cite specific instances rather than generic patterns.
- Report zero issues gracefully with coverage statistics.

## Done When

- [ ] Report emitted in-session with findings table, coverage summary, and metrics
- [ ] Severity assigned to every finding
- [ ] Constitution conflicts marked CRITICAL
- [ ] No file created or modified by this step
- [ ] Next Actions block present, with remediation offered but not applied

Next step: fix findings at their source, then re-run this step or advance to the
implement step ([command-implement.md](command-implement.md)).

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
