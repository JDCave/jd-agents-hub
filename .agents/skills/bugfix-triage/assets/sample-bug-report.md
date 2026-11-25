# Login times out after token refresh

**Reported by**: an end user through the support queue
**Environment**: web client, staging deployment, two browser tabs open

## Steps to reproduce

1. Sign in with a valid account.
2. Leave the app open until the access token refreshes in the background.
3. Open a protected page in a second browser tab.

## Expected

The protected page loads and the session stays intact.

## Actual

The request returns HTTP 500 and the page shows "session expired".

## Log excerpt

```text
TypeError: cannot read properties of undefined (reading 'token')
    at refreshSession (src/auth/session.js:42:18)
    at async onFocus (src/auth/listeners.js:17:5)
```

## Notes

The failure appears only after the refresh timer fires, and only when a second
tab is open. A single tab keeps the session alive.
