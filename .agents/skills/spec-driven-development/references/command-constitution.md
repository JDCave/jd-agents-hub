# Constitution — establish or amend project principles

Ported from spec-kit `templates/commands/constitution.md` at commit
`c43849408ac0de2ca6a52f14eaae71449776057b`; see [upstream.md](upstream.md).

Create or update `.specify/memory/constitution.md` — the guiding principles every
later step is evaluated against. Read this file only when running the constitution
step; the step order lives in `SKILL.md`.

## Inputs

The user's request in this conversation is the principle input. It may be a full
set of principles, a revision of one principle, or a description of the values the
project should hold (for example "principles focused on code quality, testing,
and security"). If the request is empty, ask for the principles before writing
anything.

## Scope Guard

This step's own work is limited to updating the project constitution itself.
Dependent page templates and command references read the constitution at runtime
and are not modified here.

- Classify every part of the user input as either constitution content or a
  separate, non-governance intent.
- If the input includes feature implementation, code generation, refactoring,
  building, or deployment requests, you **MUST NOT** execute them. Extract them
  as deferred intents instead.
- You **MUST NOT** create, modify, or delete application source files, feature
  routes, components, tests, deployment files, or other artifacts unrelated to the
  constitution workflow.
- If it is unclear whether an instruction is constitution content, ask for
  clarification before making changes.
- After completing the constitution update, include a `Next Actions` section for
  each deferred intent. List the original intent and suggest the matching next
  step (for example the specify step, [command-specify.md](command-specify.md)),
  without invoking it.
- If there are no non-governance intents, omit the `Next Actions` section.

## Outline

You are updating the project constitution at `.specify/memory/constitution.md`.
If `.specify/` does not exist yet, create the skeleton first:

```bash
python scripts/sdd_workflow.py --action bootstrap --json
```

The active constitution scaffold is resolved at step time:

```bash
python scripts/sdd_workflow.py --action resolve-template --template constitution-template --json
```

Parse `TEMPLATE_CONTENT` from the JSON. The resolver checks the project override
at `.specify/templates/constitution-template.md` first, then the bundled asset at
`assets/templates/constitution-template.md`. It **MUST** succeed before
continuing. If it fails, stop and report the resolution error; do not continue
with only one contributing template layer.

Execution flow:

1. Parse `TEMPLATE_CONTENT` as the active template.
   - If `.specify/memory/constitution.md` exists, load it as the source of current
     project-specific values and amendments. Preserve information that is still
     applicable when applying the newly resolved scaffold.
   - If it does not exist, use the resolved template as the initial document.
   - Do not write back to any versioned template layer.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user may need fewer or more principles than the template
   shows. If a number is specified, respect it and follow the general template.

2. Collect or derive values for placeholders:
   - If the user input supplies a value, use it.
   - Otherwise infer from existing repository context (README, docs, prior
     constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if
     unknown ask, or mark TODO); `LAST_AMENDED_DATE` is today if changes are made,
     otherwise keep the previous value.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: backward-incompatible governance or principle removals or
       redefinitions.
     - MINOR: a new principle or section added, or materially expanded guidance.
     - PATCH: clarifications, wording, typo fixes, non-semantic refinements.
   - If the version bump type is ambiguous, propose the reasoning before
     finalizing.

3. Draft the updated constitution using the resolved template as the required
   structure:
   - Replace every placeholder with concrete text; no bracketed tokens may be
     left except intentionally retained slots that the project has chosen not to
     define yet (justify those explicitly).
   - Preserve heading hierarchy; comments can be removed once replaced unless
     they still add clarifying guidance.
   - Ensure each Principle section has a succinct name line, a paragraph or bullet
     list capturing the non-negotiable rules, and an explicit rationale when the
     rule is not obvious.
   - Ensure the Governance section lists the amendment procedure, the versioning
     policy, and the compliance review expectations.

4. Produce a Sync Impact Report as an HTML comment at the top of the constitution
   file after the update. This report is temporary scratch material for human
   review of the amendment, not governance content; it is expected to be removed
   before the amended constitution file is committed.
   - Version change: old to new.
   - List of modified principles (old title to new title if renamed).
   - Added sections.
   - Removed sections.
   - Follow-up TODOs for any placeholders intentionally deferred.

5. Validate before final output:
   - No remaining unexplained bracket tokens.
   - The version line matches the report.
   - Dates use ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should"
     is replaced with MUST or SHOULD plus a rationale where appropriate).

6. Write the completed constitution back to `.specify/memory/constitution.md`
   (overwrite). This is the only file this step writes.

7. Output a final summary to the user with:
   - The new version and the bump rationale.
   - Any TODO placeholders or deferred items requiring manual follow-up.
   - A suggested commit message (for example
     `docs: amend constitution to vX.Y.Z (principle additions + governance update)`).
   - A `Next Actions` section for any deferred non-governance intents.

Formatting and style requirements:

- Use Markdown headings exactly as in the template (do not demote or promote
  levels).
- Wrap long rationale lines for readability (under 100 characters where
  practical) without awkward hard breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (for example only one principle revision),
still perform validation and the version decision steps.

If critical information is missing (for example the ratification date is truly
unknown), insert `TODO(<FIELD_NAME>): explanation` and include it in the Sync
Impact Report under deferred items.

Write only `.specify/memory/constitution.md`; do not create or modify template
source files.

## Done When

- [ ] Constitution written to `.specify/memory/constitution.md`
- [ ] Sync Impact Report emitted and explained
- [ ] Deferred non-governance intents listed under `Next Actions`
- [ ] Next step reported to the user

Next step: run the specify step — see [command-specify.md](command-specify.md).

> Extension hooks, presets, the `specify` CLI, and integration dispatch are not
> ported in this hub skill; see [mechanisms.md](mechanisms.md).
