# Specify — feature specification from a natural-language request

Ported from spec-kit `templates/commands/specify.md` at commit
`c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Create or update the feature specification — user scenarios, functional
requirements, success criteria, entities, assumptions. Focus on **WHAT** users
need and **WHY**, not on the stack. Read this file only when running the specify
step.

## Inputs

The text the user typed with the request **is** the feature description. Assume it
is available in this conversation. Do not ask the user to repeat it unless the
request was empty. If the description is empty, output
`ERROR "No feature description provided"` and stop.

## Outline

1. **Generate a concise short name** (2-4 words) for the feature:
   - Analyze the feature description and extract the most meaningful keywords.
   - Create a 2-4 word short name that captures the essence of the feature.
   - Use action-noun form when possible (for example `add-user-auth`,
     `fix-payment-bug`).
   - Preserve technical terms and acronyms (OAuth2, API, JWT, and similar).
   - Keep it concise but descriptive enough to understand the feature at a glance.
   - Examples:
     - "I want to add user authentication" becomes `user-auth`
     - "Implement OAuth2 integration for the API" becomes `oauth2-api-integration`
     - "Create a dashboard for analytics" becomes `analytics-dashboard`
     - "Fix payment processing timeout bug" becomes `fix-payment-timeout`

2. **Branch creation** is owned by the hub's branch/PR workflow, not by this step.

   If the user explicitly provided a branch name, note it for reference only. The
   branch name does **not** dictate the spec directory name. If the user wants a
   branch, point them at the hub's change-ticket workflow instead of creating one
   here.

3. **Create the spec feature directory**:

   Specs live under `specs/` unless the user explicitly provides
   `SPECIFY_FEATURE_DIRECTORY`.

   **Resolution order for the feature directory:**
   1. If the user explicitly provided `SPECIFY_FEATURE_DIRECTORY` (environment
      variable, argument, or configuration), use it as-is after confirming it is a
      relative path without a parent segment.
   2. Otherwise, auto-generate it under `specs/`:
      - The sequential counter is the next available three-digit number after
        scanning existing directories in `specs/`.
      - Construct the directory name as `<NNN>-<short-name>` (for example
        `003-user-auth`).

   **Create the directory and spec file** with the workflow script:

   ```bash
   python scripts/sdd_workflow.py --action new-feature --title "<feature description>" --json
   ```

   The script derives the short name, allocates the next `NNN`, writes `spec.md`
   from the resolved `spec-template` content, and persists the resolved path to
   `.specify/feature.json`:

   ```json
   {
     "feature_directory": "<resolved feature dir>"
   }
   ```

   Write the actual resolved directory value (for example `specs/003-user-auth`),
   not the literal placeholder text. This lets downstream steps locate the feature
   without relying on branch-name conventions. Use `--slug <name>` to override the
   derived short name and `--number N` to request a specific counter.

   If the template must be resolved explicitly, use:

   ```bash
   python scripts/sdd_workflow.py --action resolve-template --template spec-template --json
   ```

   Parse `TEMPLATE_CONTENT`. The resolver checks `.specify/templates/spec-template.md`
   first, then `assets/templates/spec-template.md`. Do not copy an unrelated
   template file from disk when a project override exists.

   **IMPORTANT**:
   - Create only one feature per specify invocation.
   - The spec directory name and any branch name are independent.
   - The spec directory and file are always created by this step.

4. Use `TEMPLATE_CONTENT` to understand the required sections.

5. **IF EXISTS**: Load `.specify/memory/constitution.md` for project principles and
   governance constraints.

6. Follow this execution flow:
   1. Parse the user description from the request.
      If empty: `ERROR "No feature description provided"`.
   2. Extract key concepts from the description. Identify: actors, actions, data,
      constraints.
   3. For unclear aspects:
      - Make informed guesses based on context and industry standards.
      - Only mark with `[NEEDS CLARIFICATION: specific question]` when:
        - the choice significantly impacts feature scope or user experience;
        - multiple reasonable interpretations exist with different implications;
        - no reasonable default exists.
      - **LIMIT: maximum 3 [NEEDS CLARIFICATION] markers total.**
      - Prioritize clarifications by impact: scope > security/privacy > user
        experience > technical details.
   4. Fill the User Scenarios and Testing section.
      If no clear user flow: `ERROR "Cannot determine user scenarios"`.
   5. Generate functional requirements. Each requirement must be testable. Use
      reasonable defaults for unspecified details and document the assumption in
      the Assumptions section.
   6. Define success criteria: measurable, technology-agnostic outcomes. Include
      quantitative metrics (time, performance, volume) and qualitative measures
      (user satisfaction, task completion). Each criterion must be verifiable
      without implementation details.
   7. Identify key entities when data is involved.
   8. Return SUCCESS: the spec is ready for planning.

7. Write the specification to the spec file using the template structure,
   replacing placeholders with concrete details derived from the feature
   description while preserving section order and headings.

8. **Specification quality validation**: after writing the initial spec, validate
   it against these quality criteria.

   a. **Create the spec quality checklist** at
      `<feature_dir>/checklists/requirements.md` with this structure:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Notes

      - Items marked incomplete require spec updates before the clarify step
        (see command-clarify.md) or the plan step (see command-plan.md)
      ```

   b. **Run the validation check**: review the spec against each checklist item.
      Determine pass or fail for each item and document specific issues, quoting
      the relevant spec sections.

   c. **Handle validation results**:

      - **If all items pass**: mark the checklist complete and go to the
        completion report.

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues.
        2. Update the spec to address each issue.
        3. Re-run validation until all items pass (maximum 3 iterations).
        4. If still failing after 3 iterations, document the remaining issues in
           the checklist notes and warn the user.

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all `[NEEDS CLARIFICATION: ...]` markers from the spec.
        2. **LIMIT CHECK**: if more than 3 markers exist, keep only the 3 most
           critical (by scope, security, and UX impact) and make informed guesses
           for the rest.
        3. For each clarification needed (maximum 3), present options to the user
           in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - table formatting**: ensure markdown tables are properly
           formatted:
           - Use consistent spacing with pipes aligned.
           - Each cell has spaces around its content: `| Content |`, not `|Content|`.
           - The header separator has at least three dashes: `|--------|`.
           - Check that the table renders correctly in markdown preview.
        5. Number questions sequentially (Q1, Q2, Q3 - maximum 3 total).
        6. Present all questions together before waiting for responses.
        7. Wait for the user to answer all questions (for example
           "Q1: A, Q2: Custom - [details], Q3: B").
        8. Update the spec by replacing each `[NEEDS CLARIFICATION]` marker with
           the user's selected or provided answer.
        9. Re-run validation after all clarifications are resolved.

   d. **Update the checklist** after each validation iteration with the current
      pass/fail status.

## Completion Report

Report completion to the user with:
- The feature directory path and the spec file path.
- A checklist results summary.
- Readiness for the next step: clarify ([command-clarify.md](command-clarify.md))
  or plan ([command-plan.md](command-plan.md)).

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no stack, APIs, or code structure).
- Write for business stakeholders, not implementation specialists.
- Do NOT create checklists that are embedded in the spec. That is the separate
  checklist step.

### Section Requirements

- **Mandatory sections**: must be completed for every feature.
- **Optional sections**: include only when relevant to the feature.
- When a section does not apply, remove it entirely; do not leave it as "N/A".

### For AI Generation

When creating this spec from a user request:

1. **Make informed guesses**: use context, industry standards, and common
   patterns to fill gaps.
2. **Document assumptions**: record reasonable defaults in the Assumptions
   section.
3. **Limit clarifications**: maximum 3 `[NEEDS CLARIFICATION]` markers, used only
   for critical decisions that significantly impact scope or user experience,
   have multiple reasonable interpretations with different implications, or lack
   any reasonable default.
4. **Prioritize clarifications**: scope > security/privacy > user experience >
   technical details.
5. **Think like a tester**: every vague requirement should fail the "testable and
   unambiguous" checklist item.
6. **Common areas needing clarification** (only when no reasonable default
   exists):
   - Feature scope and boundaries (include or exclude specific use cases).
   - User types and permissions when multiple conflicting interpretations exist.
   - Security or compliance requirements when legally or financially significant.

**Examples of reasonable defaults** (do not ask about these):

- Data retention: industry-standard practice for the domain.
- Performance targets: standard web or mobile expectations unless specified.
- Error handling: user-friendly messages with appropriate fallbacks.
- Authentication method: standard session-based or OAuth2 for web apps.
- Integration patterns: project-appropriate patterns (REST or GraphQL for web
  services, function calls for libraries, CLI arguments for utilities).

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: include specific metrics (time, percentage, count, rate).
2. **Technology-agnostic**: no mention of frameworks, languages, databases, or
   utilities.
3. **User-focused**: describe outcomes from the user or business perspective, not
   system internals.
4. **Verifiable**: testable without knowing implementation details.

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical; use "Users see results
  instantly")
- "Database can handle 1000 TPS" (implementation detail; use a user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)

## Done When

- [ ] Specification written to the spec file and validated against the quality
      checklist
- [ ] Requirements checklist created at `<feature_dir>/checklists/requirements.md`
- [ ] Completion reported to the user with feature directory, spec file path, and
      checklist results

Next step: run the clarify step when ambiguity remains
([command-clarify.md](command-clarify.md)), otherwise run the plan step
([command-plan.md](command-plan.md)).

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
