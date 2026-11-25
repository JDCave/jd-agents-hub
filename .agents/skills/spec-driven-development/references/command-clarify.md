# Clarify — resolve spec ambiguity before planning

Ported from spec-kit `templates/commands/clarify.md` at commit
`c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Goal: detect and reduce ambiguity or missing decision points in the active feature
specification, and record the clarifications directly in the spec file. Read this
file only when running the clarify step.

Note: this workflow is expected to run (and complete) before the plan step. If the
user explicitly states they are skipping clarification (for example an exploratory
spike), proceed but warn that downstream rework risk increases.

## Execution Steps

1. Resolve the feature paths once:

   ```bash
   python scripts/sdd_workflow.py --action prereqs --json
   ```

   Parse `FEATURE_DIR`, `FEATURE_SPEC`, and optionally `IMPL_PLAN` and `TASKS`
   for chained flows. If the JSON parsing fails or the feature is missing, abort
   and instruct the user to re-run the specify step
   ([command-specify.md](command-specify.md)).

2. **IF EXISTS**: Load `.specify/memory/constitution.md` for project principles and
   governance constraints.

3. Load the current spec file. Perform a structured ambiguity and coverage scan
   using this taxonomy. For each category, mark the status: Clear, Partial, or
   Missing. Produce an internal coverage map used for prioritization (do not output
   the raw map unless no questions will be asked).

   Functional Scope and Behavior:
   - Core user goals and success criteria.
   - Explicit out-of-scope declarations.
   - User roles and persona differentiation.

   Domain and Data Model:
   - Entities, attributes, relationships.
   - Identity and uniqueness rules.
   - Lifecycle and state transitions.
   - Data volume and scale assumptions.

   Interaction and UX Flow:
   - Critical user journeys and sequences.
   - Error, empty, and loading states.
   - Accessibility or localization notes.

   Non-Functional Quality Attributes:
   - Performance (latency, throughput targets).
   - Scalability (horizontal or vertical, limits).
   - Reliability and availability (uptime, recovery expectations).
   - Observability (logging, metrics, tracing signals).
   - Security and privacy (authentication and authorization, data protection,
     threat assumptions).
   - Compliance or regulatory constraints, if any.

   Integration and External Dependencies:
   - External services and APIs, plus failure modes.
   - Data import and export formats.
   - Protocol and versioning assumptions.

   Edge Cases and Failure Handling:
   - Negative scenarios.
   - Rate limiting and throttling.
   - Conflict resolution (for example concurrent edits).

   Constraints and Tradeoffs:
   - Technical constraints (language, storage, hosting).
   - Explicit tradeoffs or rejected alternatives.

   Terminology and Consistency:
   - Canonical glossary terms.
   - Avoided synonyms and deprecated terms.

   Completion Signals:
   - Acceptance criteria testability.
   - Measurable definition-of-done indicators.

   Misc and Placeholders:
   - TODO markers and unresolved decisions.
   - Ambiguous adjectives ("robust", "intuitive") that lack quantification.

   For each category with Partial or Missing status, add a candidate question
   opportunity unless clarification would not materially change implementation or
   validation strategy, or the item is specifically about implementation method,
   stack comparison, or task breakdown.

4. Generate internally a prioritized queue of candidate clarification questions
   (maximum 5). Do NOT output them all at once. Apply these constraints:
   - Maximum of 5 total questions across the whole session.
   - Each question must be answerable with EITHER a short multiple-choice
     selection (2-5 distinct, mutually exclusive options) OR a one-word or
     short-phrase answer (constrain explicitly: "Answer in <=5 words").
   - Only include questions whose answers materially impact architecture, data
     modeling, task decomposition, test design, UX behavior, operational
     readiness, or compliance validation.
   - Keep category coverage balanced: cover the highest-impact unresolved
     categories first; avoid two low-impact questions while a single high-impact
     area (for example security posture) remains unresolved.
   - Exclude questions already answered, trivial stylistic preferences, and
     plan-level execution details unless they block correctness.
   - Favor clarifications that reduce downstream rework risk or prevent misaligned
     acceptance tests.
   - If more than 5 categories remain unresolved, select the top 5 by the
     impact-times-uncertainty heuristic.

5. Sequential questioning loop (interactive):
   - Present EXACTLY ONE question at a time.
   - **Question writing quality** applies to every question, multiple-choice or
     short-answer:
     - Lead with `**Question:**` followed by a full interrogative that ends with
       `?`. The question text before the `?` must make sense on its own.
     - NEVER use a topic label, section heading, or requirement id as the question
       itself. For example, `Acceptance device/runtime matrix (FR-023)` is
       INVALID: it is a label, not a question.
     - After the `?`, the only permitted suffix is an optional parenthesized
       requirement or question id. Exact format: `**Question:** <interrogative>?`
       or `**Question:** <interrogative>? (FR-023)`. Never put the id before the
       `?`, and never use the id alone as the whole prompt.
     - Immediately after the question line, add one plain-language "Why it
       matters" sentence (the stake for acceptance or shipping) before the
       recommendation and options.
     - Use everyday wording; introduce jargon only when defined in the same
       sentence. Self-check: a reader who does not know the process must be able
       to answer from the Question line alone. Terse is fine; cryptic labels are
       not.
   - For multiple-choice questions:
     - **Analyze all options** and determine the **most suitable option** based on
       best practice for the project type, common patterns in similar
       implementations, risk reduction (security, performance, maintainability),
       and alignment with explicit goals or constraints visible in the spec.
     - Present the **recommended option prominently** at the top with clear
       reasoning: `**Recommended:** Option [X] - <reasoning>`.
     - Then render all options as a Markdown table:

       | Option | Description |
       |--------|-------------|
       | A | <Option A description> |
       | B | <Option B description> |
       | C | <Option C description> (add D and E as needed, up to 5) |
       | Short | Provide a different short answer (<=5 words) (include only if a free-form alternative is appropriate) |

     - After the table add: `You can reply with the option letter (e.g. "A"),
       accept the recommendation by saying "yes" or "recommended", or provide your
       own short answer.`
   - For short-answer style (no meaningful discrete options):
     - Provide a **suggested answer** based on best practice and context:
       `**Suggested:** <your proposed answer> - <brief reasoning>`.
     - Then output: `Format: Short answer (<=5 words). You can accept the
       suggestion by saying "yes" or "suggested", or provide your own answer.`
   - After the user answers:
     - If the user replies with "yes", "recommended", or "suggested", use the
       previously stated recommendation or suggestion as the answer.
     - Otherwise validate that the answer maps to one option or fits the <=5 word
       constraint.
     - If the answer is ambiguous, ask for a quick disambiguation; the retry
       still belongs to the same question and does not advance the queue.
     - Once satisfactory, record it in working memory (do not write to disk yet)
       and move to the next queued question.
   - Stop asking questions when:
     - all critical ambiguities are resolved early (remaining queued items become
       unnecessary), or
     - the user signals completion ("done", "good", "no more"), or
     - 5 questions have been asked.
   - Never reveal future queued questions in advance.
   - If no valid questions exist at the start, immediately report no critical
     ambiguities.

6. Integrate after EACH accepted answer (incremental update approach):
   - Maintain an in-memory representation of the spec, loaded once at the start,
     plus the raw file contents.
   - For the first integrated answer in this session:
     - Ensure a `## Clarifications` section exists; create it just after the
       highest-level contextual or overview section per the spec template if
       missing.
     - Under it, create (if not present) a `### Session YYYY-MM-DD` subheading for
       today.
   - Append a bullet line immediately after acceptance:
     `- Q: <question> → A: <final answer>`.
   - Then immediately apply the clarification to the most appropriate section:
     - Functional ambiguity: update or add a bullet in Functional Requirements.
     - User interaction or actor distinction: update User Stories or the Actors
       subsection (if present) with the clarified role, constraint, or scenario.
     - Data shape or entities: update the Data Model (add fields, types,
       relationships) while preserving ordering; note added constraints
       succinctly.
     - Non-functional constraint: add or modify a measurable criterion in Success
       Criteria, converting a vague adjective to a metric or explicit target.
     - Edge case or negative flow: add a new bullet under Edge Cases or Error
       Handling, or create that subsection when the template provides a
       placeholder for it.
     - Terminology conflict: normalize the term across the spec; retain the
       original only when necessary by adding `(formerly referred to as "X")`
       once.
   - If the clarification invalidates an earlier ambiguous statement, replace that
     statement instead of duplicating it; leave no obsolete contradictory text.
   - Save the spec file AFTER each integration to minimize the risk of context
     loss (atomic overwrite).
   - Preserve formatting: do not reorder unrelated sections and keep the heading
     hierarchy intact.
   - Keep each inserted clarification minimal and testable to avoid narrative
     drift.

7. Validate after EACH write plus a final pass:
   - The Clarifications session contains exactly one bullet per accepted answer,
     with no duplicates.
   - Total asked and accepted questions is at most 5.
   - Updated sections contain no lingering vague placeholders that the new answer
     was meant to resolve.
   - No contradictory earlier statement remains (scan for now-invalid
     alternatives that should have been removed).
   - Markdown structure is valid; the only allowed new headings are
     `## Clarifications` and `### Session YYYY-MM-DD`.
   - Terminology consistency: the same canonical term is used across all updated
     sections.

8. Write the updated spec back to `FEATURE_SPEC`.

9. **Re-validate the spec quality checklist** when it exists:
   - Check whether `<feature_dir>/checklists/requirements.md` exists. If it does
     not, skip this step silently.
   - If it exists:
     1. Read the checklist file.
     2. Identify all task-list checkbox lines: lines matching `- [ ]`, `- [x]`,
        or `- [X]` (case-insensitive, tolerant of leading whitespace for nested
        items) outside code fences. Ignore all other content.
     3. For each checkbox line, record its current marker state and item text in a
        before-snapshot list.
     4. Re-evaluate each checkbox item against the **updated** spec saved in step
        8.
     5. Update an item only when its state actually changes:
        - If the item now passes and was unchecked, change `[ ]` to `[x]`.
        - If the item now fails and was checked, change `[x]` or `[X]` to `[ ]`.
        - If the state is unchanged, leave the marker as-is to avoid cosmetic
          diffs.
     6. Save the updated checklist file. **Only toggle the marker portion** of
        checkbox lines whose state changed. All other content, including
        headings, metadata, notes, line ordering, and whitespace, must remain
        unchanged.
     7. Compare the before-snapshot with the current state to compute three lists
        for the completion report: newly passing, regressions, and still
        unchecked.
     8. Record the before and after pass counts as checked over total items (for
        example "12/16 to 15/16 items passing").

Behavior rules:

- If no meaningful ambiguities are found (or all potential questions would be
  low-impact), respond: "No critical ambiguities detected worth formal
  clarification." and suggest proceeding.
- If the spec file is missing, instruct the user to run the specify step first
  ([command-specify.md](command-specify.md)); do not create a new spec here.
- Never exceed 5 total asked questions; retries for a single question do not count
  as new questions.
- Avoid speculative stack questions unless the absence blocks functional clarity.
- Respect early termination signals ("stop", "done", "proceed").
- If no questions are asked because coverage is complete, output a compact
  coverage summary (all categories Clear), then suggest advancing.
- If the quota is reached with unresolved high-impact categories remaining, flag
  them explicitly under Deferred with a rationale.

Context for prioritization: the user's optional focus text in this conversation.

## Completion Report

Report completion after the questioning loop ends or the user terminates early:
- Number of questions asked and answered.
- Path to the updated spec.
- Sections touched (list names).
- Spec quality checklist status when it was re-validated: before and after pass
  counts, items that changed state in either direction, and any items still
  unchecked.
- Coverage summary table listing each taxonomy category with status: Resolved (was
  Partial or Missing and addressed), Deferred (exceeds the question quota, or the
  remaining item is an implementation method, stack comparison, or task
  breakdown), Clear (already sufficient), or Outstanding (still Partial or
  Missing but low impact).
- If any Outstanding or Deferred items remain, recommend whether to proceed to the
  plan step or run clarify again later after planning.
- Suggested next step.

## Done When

- [ ] Spec ambiguities identified and clarifications integrated into the spec file
- [ ] Spec quality checklist re-validated against the updated spec when it exists
- [ ] Completion reported with questions answered, sections touched, checklist
      status, and coverage summary

Next step: run the plan step — see [command-plan.md](command-plan.md).

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
