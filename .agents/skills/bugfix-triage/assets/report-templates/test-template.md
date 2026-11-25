# Bug Verification: <short title>

- **Slug**: <BUG_SLUG>
- **Tested**: <ISO 8601 date>
- **Assessment**: ./assessment.md
- **Fix**: ./fix.md
- **Result**: <verified | partial | failed | not-run>

## Summary

<One or two sentences: does the bug still reproduce, did the fix hold, were any regressions found.>

## Checks Performed

| Check | Command / Action | Result | Notes |
|-------|------------------|--------|-------|
| Reproduction (post-fix) | <command or manual steps> | pass / fail / skipped / not-run | <short note> |
| New / updated tests | `<command>` | pass / fail | <short note> |
| Regression suite | `<command>` | pass / fail / skipped | <short note> |
| Lint / type-check | `<command>` | pass / fail / skipped | <short note> |

## Output Excerpts

<Short snippets of relevant output, such as the final summary line of a test run or the failing assertion. Keep it tight — no full logs.>

## Residual Risks

- <known limitation, environment not covered, untested path>

## Recommendation

<One paragraph. Examples:>
- "Close the bug — verified end-to-end."
- "Hold — reproduction inconclusive; verify in staging."
- "Reopen — symptom still reproduces; re-run the assess stage with the evidence recorded here."
