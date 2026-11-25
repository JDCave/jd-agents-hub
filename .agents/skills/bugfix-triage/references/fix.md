# Stage 2 — Fix the bug

Run this stage with `references/fix.md` open. It applies the remediation that the
assessment proposed and records the changes in `.specify/bugs/<slug>/fix.md`.
This is the **only** stage that edits source code.

## Slug resolution

Resolve the working slug in this order, stopping at the first match:

1. **Explicit user input** — a slug passed as `--slug <slug>`, `slug=<slug>`, or
   a bare slug-like token.
2. **Conversation context** — if the session just ran the assess stage, the slug
   it reported is the working slug. Reuse it without re-prompting, and confirm it
   by checking that `.specify/bugs/<slug>/assessment.md` exists; if it does not,
   fall through.
3. **Single candidate on disk** — if exactly one bug has an `assessment.md`, use
   the slug from its parent directory.
4. **Disambiguate** — interactive mode asks the user which bug to fix and lists
   the candidates; automated mode stops with an error listing the candidates.
   Do not guess.

State briefly which resolution path was used (explicit, from context, single
candidate, or asked). Inspect the workspace with the bundled utility, relative
to this skill folder:

```bash
python scripts/bug_workflow.py --action check --slug <slug>
python scripts/bug_workflow.py --action report --slug <slug>
```

## Prerequisites

- `.specify/bugs/<slug>/assessment.md` must exist. If it does not, stop and
  instruct the user to run the assess stage first.
- If `fix.md` already exists, ask the user whether to overwrite it before
  continuing (interactive mode) or refuse (automated mode).
- Read `assessment.md` in full. Treat its **Proposed Remediation**, **Files
  likely to change**, **Tests to add or update**, and **Risks & Considerations**
  sections as the contract for this stage.

## Execution

1. **Confirm the plan**
   - Restate, in 3–6 bullets, what is about to change and where, based on the
     assessment.
   - If the assessment's verdict is `invalid`, stop — there is nothing to fix.
     Tell the user and exit.
   - If the verdict is `likely valid, needs reproduction` and there are
     unresolved `[NEEDS CLARIFICATION]` items, flag them and ask the user
     whether to proceed in interactive mode, or stop in automated mode.

2. **Apply the remediation**
   - Make the code changes described by the preferred remediation. Stay within
     the files listed by the assessment unless newly discovered evidence
     requires expanding scope; log every expansion explicitly in the fix report.
   - Add or update the tests called out in the assessment so the bug cannot
     regress silently.
   - Keep the change minimal — do not refactor unrelated code and do not
     introduce dependencies that the assessment did not call for.
   - If the assessment turns out to be wrong (the proposed fix does not work,
     the root cause is elsewhere), STOP modifying code, document the new finding
     in the fix report under **Deviations from Assessment**, and recommend
     re-running the assess stage.

3. **Run local checks**
   - If the project has obvious test commands (for example `pytest`, a package
     test task, or a build test target), run the tests that exercise the changed
     paths. Capture pass or fail and the key output.
   - Do not run destructive or network-dependent suites without the user's
     consent.

4. **Write the fix report**

   Write to `.specify/bugs/<slug>/fix.md` using
   `assets/report-templates/fix-template.md` as the schema. The metadata block
   must carry `Slug`, `Fixed`, `Assessment`, and `Status`; the status vocabulary
   is exactly `applied`, `partial`, `not-applied`. Keep every required section:
   Summary, Changes, Diff Highlights (optional), Tests Added or Updated, Local
   Verification, Deviations from Assessment, Follow-ups.

## Guardrails

- Never modify files outside the project workspace.
- Never edit `assessment.md` — it is the contract this stage works against.
  Record disagreements in `fix.md` under **Deviations from Assessment**.
- Never delete files unless the assessment explicitly required it.
- Never overwrite an existing `fix.md` without confirmation.
- Never claim a fix that was not applied. Use `partial` or `not-applied` when
  the change could not be completed, and say why.
- Report to the user the slug, the `fix.md` path, the status, and the next step:
  run the test stage with `--slug <slug>`.
