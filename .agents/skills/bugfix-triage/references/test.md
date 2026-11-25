# Stage 3 — Test the fix

Run this stage with `references/test.md` open. It validates that the fix recorded
by the fix stage actually resolves the bug described by the assess stage, and it
writes the verification report at `.specify/bugs/<slug>/test.md`. This stage
never edits source code.

## Slug resolution

Resolve the working slug in this order, stopping at the first match:

1. **Explicit user input** — a slug passed as `--slug <slug>`, `slug=<slug>`, or
   a bare slug-like token.
2. **Conversation context** — if the session just ran the assess or fix stage,
   reuse the slug it reported, confirmed by `.specify/bugs/<slug>/fix.md`
   existing; if it does not, fall through.
3. **Single candidate on disk** — if exactly one bug has a `fix.md`, use it.
4. **Disambiguate** — interactive mode asks the user which bug to validate and
   lists the candidates; automated mode stops with an error listing the
   candidates. Do not guess.

State briefly which resolution path was used. Inspect the workspace first with
the bundled utility, relative to this skill folder:

```bash
python scripts/bug_workflow.py --action check --slug <slug>
```

The check action reports the next stage and rejects verdict values outside the
documented vocabulary.

## Prerequisites

- `.specify/bugs/<slug>/assessment.md` must exist.
- `.specify/bugs/<slug>/fix.md` must exist. If not, stop and instruct the user
  to run the fix stage first.
- If `test.md` already exists, ask the user whether to overwrite it (interactive
  mode) or refuse (automated mode).
- Read both `assessment.md` and `fix.md` in full so the original symptom,
  reproduction steps, code changes, and added tests are known.

## Execution

1. **Plan the validation**
   - Decide which checks prove the bug is gone:
     - Re-run the reproduction steps from the assessment, or their automated
       equivalent.
     - Run the tests added or updated in the fix.
     - Run any broader regression suite that touches the changed files.
   - Decide which checks prove nothing was broken: existing suites for the
     changed modules, plus lint or type-check when the project uses them.

2. **Run the checks**
   - Execute each planned check. Capture the command, exit status, and a short
     excerpt of relevant output (last few lines, or the failing assertion).
   - If a check is destructive, network-dependent, or expensive, skip it and
     record it as `skipped` with a reason; do not run it without explicit user
     consent.
   - If a check cannot be run at all (missing tooling, no test framework
     configured), record it as `not-run` with a reason instead of fabricating a
     result.

3. **Judge the outcome**
   - Mark the fix as:
     - **verified** — all critical checks pass and the original symptom no
       longer reproduces.
     - **partial** — the original symptom is gone but unrelated regressions
       appeared, or some checks are inconclusive.
     - **failed** — the symptom still reproduces or the regression suite is
       broken by the fix.
     - **not-run** — verification could not be exercised at all; record why.
   - Do not over-claim. If reproduction was not actually performed (for example,
     the bug needed a production environment), say so explicitly and downgrade
     the result. Always downgrade to `partial` when the assessment listed a
     reproduction that was not actually exercised.

4. **Write the verification report**

   Write to `.specify/bugs/<slug>/test.md` using
   `assets/report-templates/test-template.md` as the schema. The metadata block
   must carry `Slug`, `Tested`, `Assessment`, `Fix`, and `Result`; the result
   vocabulary is exactly `verified`, `partial`, `failed`, `not-run`. Keep every
   required section: Summary, Checks Performed, Output Excerpts, Residual Risks,
   Recommendation.

## Guardrails

- This stage must not modify source code. It only runs checks and writes inside
  `.specify/bugs/<slug>/`.
- Never overwrite an existing `test.md` without confirmation.
- Never mark a fix as `verified` based on tests alone when the original
  assessment listed a reproduction that was not actually exercised — downgrade
  to `partial` and say so.
- On a `failed` result, recommend re-running the assess stage with the new
  evidence captured in `test.md`.
- Report to the user the slug, the `test.md` path, the result, and the
  recommendation.
