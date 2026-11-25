# Tasks — dependency-ordered executable task list

Ported from spec-kit `templates/commands/tasks.md` and `templates/tasks-template.md`
at commit `c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Generate an actionable, dependency-ordered `tasks.md` for the feature from the
available design artifacts, organized by user story so each story is independently
implementable and testable. Read this file only when running the tasks step.

## Outline

1. **Setup**: resolve the paths and copy the tasks template:

   ```bash
   python scripts/sdd_workflow.py --action prereqs --json
   python scripts/sdd_workflow.py --action tasks --json
   ```

   Parse `FEATURE_DIR`, `TASKS`, and the `AVAILABLE_DOCS` list. The `tasks` action
   copies the resolved `tasks-template` into `<feature_dir>/tasks.md`; it exits 2
   when `tasks.md` already exists unless `--force` is passed. Resolve the template
   content explicitly when needed:

   ```bash
   python scripts/sdd_workflow.py --action resolve-template --template tasks-template --json
   ```

   `plan.md` and `spec.md` must exist. When either is missing, stop and report
   which step to run first: specify for a missing spec, plan for a missing plan.

2. **Load design documents** from `FEATURE_DIR`:
   - **Required**: `plan.md` (stack, libraries, structure) and `spec.md` (user
     stories with priorities).
   - **Optional**: `data-model.md` (entities), `contracts/` (interface contracts),
     `research.md` (decisions), `quickstart.md` (test scenarios).
   - **IF EXISTS**: load `.specify/memory/constitution.md` for project principles
     and governance constraints.
   - Not every project has every document. Generate tasks from what is available.

3. **Execute the task-generation workflow**:
   - Load `plan.md` and extract the stack, libraries, and project structure.
   - Load `spec.md` and extract user stories with their priorities (P1, P2, P3).
   - When `data-model.md` exists, extract entities and map them to user stories.
   - When `contracts/` exists, map interface contracts to user stories.
   - When `research.md` exists, extract decisions for setup tasks.
   - Generate tasks organized by user story (see the Task Generation Rules).
   - Generate a dependency graph showing user story completion order.
   - Create parallel execution examples per user story.
   - Validate task completeness: each user story has all needed tasks and is
     independently testable.

4. **Generate `tasks.md`** using the template content as the structure. Fill in:
   - The correct feature name from `plan.md`.
   - Phase 1: setup tasks (project initialization).
   - Phase 2: foundational tasks (blocking prerequisites for all user stories).
   - Phase 3 and later: one phase per user story in priority order from `spec.md`.
   - Each phase includes the story goal, independent test criteria, tests when
     requested, and implementation tasks.
   - Final phase: polish and cross-cutting concerns.
   - All tasks follow the strict checklist format (see the rules below).
   - Clear file paths for each task.
   - A dependencies section showing story completion order.
   - Parallel execution examples per story.
   - An implementation strategy section (MVP first, incremental delivery).

## Completion Report

Output the path to the generated `tasks.md` and a summary with:
- Total task count.
- Task count per user story.
- Parallel opportunities identified.
- Independent test criteria for each story.
- Suggested MVP scope, typically just User Story 1.
- Format validation: confirm that ALL tasks follow the checklist format
  (checkbox, id, labels, file paths).

Context for task generation: the user's optional context in this conversation.

The `tasks.md` must be immediately executable: each task must be specific enough
that an agent can complete it without additional context.

## Task Generation Rules

**CRITICAL**: tasks MUST be organized by user story to enable independent
implementation and testing.

**Tests are OPTIONAL**: only generate test tasks when the feature specification or
the user explicitly requests a test-first approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox).
2. **Task ID**: sequential number (T001, T002, T003) in execution order.
3. **[P] marker**: include ONLY when the task is parallelizable (different files,
   no dependencies on incomplete tasks).
4. **[Story] label**: REQUIRED for user story phase tasks only.
   - Format: [US1], [US2], [US3], mapping to the user stories from `spec.md`.
   - Setup phase: NO story label.
   - Foundational phase: NO story label.
   - User story phases: MUST have a story label.
   - Polish phase: NO story label.
5. **Description**: a clear action with the exact file path.

**Examples**:

- CORRECT: `- [ ] T001 Create project structure per implementation plan`
- CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- WRONG: `- [ ] Create User model` (missing id and story label)
- WRONG: `T001 [US1] Create model` (missing checkbox)
- WRONG: `- [ ] [US1] Create User model` (missing task id)
- WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From user stories in `spec.md`** (primary organization):
   - Each user story (P1, P2, P3) gets its own phase.
   - Map all related components to their story: models, services, interfaces or
     UI, and tests when requested.
   - Mark story dependencies; most stories should be independent.

2. **From contracts**:
   - Map each interface contract to the user story it serves.
   - When tests are requested, each interface contract gets a contract-test task
     marked [P] before implementation in that story's phase.

3. **From the data model**:
   - Map each entity to the user story or stories that need it.
   - When an entity serves multiple stories, put it in the earliest story or in
     the setup phase.
   - Relationships become service-layer tasks in the appropriate story phase.
   - For each field with constraints in `data-model.md` (maximum length,
     nullable or required, enum values, validation rules), quote the constraint
     verbatim in the task description so it is not left to implementation-time
     discretion.

4. **From setup and infrastructure**:
   - Shared infrastructure goes into the setup phase (Phase 1).
   - Foundational and blocking tasks go into the foundational phase (Phase 2).
   - Story-specific setup belongs inside that story's phase.

### Phase Structure

- **Phase 1**: setup (project initialization).
- **Phase 2**: foundational (blocking prerequisites that MUST complete before user
  stories).
- **Phase 3 and later**: user stories in priority order (P1, P2, P3).
  - Within each story: tests when requested, then models, then services, then
    endpoints, then integration.
  - Each phase should be a complete, independently testable increment.
- **Final phase**: polish and cross-cutting concerns.

## Done When

- [ ] `tasks.md` generated with all phases, task ids, and file paths
- [ ] Every task matches the strict checklist format
- [ ] Dependency graph, parallel examples, and MVP scope recorded
- [ ] Completion reported with task count, story breakdown, and MVP scope

Next step: run the analyze step ([command-analyze.md](command-analyze.md)) to check
cross-artifact consistency, then the implement step
([command-implement.md](command-implement.md)).

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
