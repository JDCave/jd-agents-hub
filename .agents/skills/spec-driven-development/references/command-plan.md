# Plan — technical plan and design artifacts

Ported from spec-kit `templates/commands/plan.md` and `templates/plan-template.md`
at commit `c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Turn the spec and constitution into a technical implementation plan, research, data
model, contracts, and a runnable quickstart. This is where implementation detail
belongs. Read this file only when running the plan step.

## Outline

1. **Setup**: copy the plan page template into the current feature and resolve the
   feature paths:

   ```bash
   python scripts/sdd_workflow.py --action plan --json
   python scripts/sdd_workflow.py --action prereqs --json
   ```

   Parse `FEATURE_DIR`, `IMPL_PLAN`, `FEATURE_SPEC`, and `TASKS`. The `plan` action
   copies the resolved `plan-template` into `<feature_dir>/plan.md`; it exits 2
   when `plan.md` already exists unless `--force` is passed. Resolve the template
   content explicitly when needed:

   ```bash
   python scripts/sdd_workflow.py --action resolve-template --template plan-template --json
   ```

2. **Load context**: read `FEATURE_SPEC` and `.specify/memory/constitution.md`.
   Load the `IMPL_PLAN` template already copied into the feature directory.

3. **Execute the plan workflow**: follow the structure in the `IMPL_PLAN`
   template to:
   - Fill Technical Context, marking unknowns as `NEEDS CLARIFICATION`.
   - Fill the Constitution Check section from the constitution.
   - Evaluate the gate: **ERROR** if violations are unjustified.
   - Phase 0: generate `research.md` and resolve all `NEEDS CLARIFICATION` items.
   - Phase 1: generate `data-model.md`, `contracts/`, and `quickstart.md`.
   - Re-evaluate the Constitution Check after design.

## Completion Report

This step ends after Phase 1 design. Report the feature directory, the
`IMPL_PLAN` path, and the generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**:
   - Every `NEEDS CLARIFICATION` item becomes a research task.
   - Every dependency becomes a best-practice task.
   - Every integration becomes a patterns task.

2. **Generate and dispatch research tasks**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using this format:
   - Decision: [what was chosen]
   - Rationale: [why it was chosen]
   - Alternatives considered: [what else was evaluated]

   **Output**: `research.md` with all `NEEDS CLARIFICATION` items resolved.

### Phase 1: Design & Contracts

**Prerequisites**: `research.md` is complete.

1. **Extract entities from the feature spec** into `data-model.md`:
   - Entity name, fields, relationships.
   - Validation rules from requirements.
   - State transitions when applicable.

2. **Define interface contracts** (when the project has external interfaces) into
   `contracts/`:
   - Identify what interfaces the project exposes to users or other systems.
   - Document the contract format appropriate for the project type.
   - Examples: public APIs for libraries, command schemas for CLI utilities,
     endpoints for web services, grammars for parsers, UI contracts for
     applications.
   - Skip this artifact when the project is purely internal.

3. **Create the quickstart validation guide** as `quickstart.md`:
   - Document runnable validation scenarios that prove the feature works
     end-to-end.
   - Include prerequisites, setup commands, test and run commands, and expected
     outcomes.
   - Link to contracts and data-model details instead of duplicating them.
   - Do not include full implementation code, model or service bodies,
     migrations, or complete test suites.
   - Keep this artifact as a validation and run guide; implementation detail
     belongs in `tasks.md` and the implementation step.

   **Output**: `data-model.md`, `contracts/*`, and `quickstart.md`.

## Key Rules

- Use absolute paths for filesystem operations; use project-relative paths in
  documentation.
- ERROR on gate failures or unresolved clarifications.

## Done When

- [ ] Plan workflow executed and design artifacts generated
- [ ] Constitution Check passed before Phase 0 and re-checked after Phase 1
- [ ] All `NEEDS CLARIFICATION` items resolved in `research.md`
- [ ] Completion reported with the feature directory, plan path, and generated
      artifacts

Next step: run the tasks step — see [command-tasks.md](command-tasks.md). The
optional checklist step ([command-checklist.md](command-checklist.md)) can run in
between to review requirements quality.

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
