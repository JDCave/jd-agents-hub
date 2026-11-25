# Bug Assessment: Login times out after token refresh

- **Slug**: login-timeout
- **Created**: <ISO 8601 date>
- **Source**: assets/sample-bug-report.md
- **Verdict**: valid
- **Severity**: high

## Report (verbatim or summarized)

A support report describes the session being dropped after the access token
refreshes. The log excerpt shows an undefined `token` value read inside
`refreshSession` (`src/auth/session.js:42`).

## Symptom

A protected page returns HTTP 500 after the background token refresh, while the
same page loads normally before the refresh timer fires.

## Reproduction

1. Sign in with a valid account.
2. Leave the app open until the access token refreshes.
3. Open a protected page in a second browser tab.
4. Observe the HTTP 500 response and the "session expired" message.

## Suspected Code Paths

- `src/auth/session.js:42` — reads `session.token` before the refresh promise resolves
- `src/auth/listeners.js:17` — triggers the refresh from a focus handler without awaiting it

## Root Cause Hypothesis

The focus listener starts a refresh and immediately reads the session, so the
second tab observes a half-updated session object. Confidence: medium.

## Proposed Remediation

**Preferred**: await the refresh promise before any caller reads the session,
and return the cached session when a refresh is already in flight.

**Files likely to change**:
- `src/auth/session.js`
- `src/auth/listeners.js`
- `tests/auth/session.test.js`

**Tests to add or update**:
- a concurrent-refresh test that opens two callers and asserts both receive the
  same resolved session.

## Risks & Considerations

- The auth module is used by every page; keep the change small and covered.
- A refresh lock must be released on failure so the next attempt can retry.

## URL Trust Record

- **URL supplied**: none
- **Host**: not applicable
- **Policy branch**: not-applicable

## Open Questions

- [NEEDS CLARIFICATION: does the same failure appear on the first focus event, or only after the timer fires?]
