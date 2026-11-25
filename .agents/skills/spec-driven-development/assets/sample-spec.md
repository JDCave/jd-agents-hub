# Feature Specification: User authentication

**Feature Branch**: `001-add-user-auth`

**Created**: 2026-01-15

**Status**: Draft

**Input**: User description: "Add user authentication so saved items survive a browser session."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create an account (Priority: P1)

A new user creates an account with an email address and a password.

**Why this priority**: Without an account there is nothing to sign in to.

**Independent Test**: Create an account from a clean session and confirm the saved list is empty but reachable.

**Acceptance Scenarios**:

1. **Given** no account, **When** the visitor submits a valid email and password, **Then** the account exists and the visitor is signed in.

---

### User Story 2 - Sign in again (Priority: P2)

A returning user signs in and sees the saved items from the previous session.

**Why this priority**: The feature only delivers value when state survives a session.

**Independent Test**: Sign out, sign in with the same credentials, and confirm saved items are still listed.

**Acceptance Scenarios**:

1. **Given** an existing account, **When** the user signs in, **Then** the saved items are listed.

### Edge Cases

- Wrong password: the user sees a generic failure message and stays signed out.
- Expired session: the user is asked to sign in again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let a visitor create an account with a unique email address.
- **FR-002**: System MUST authenticate a returning user with the stored credential.
- **FR-003**: System MUST keep a signed-in session for 30 days on a trusted device.
- **FR-004**: System MUST reject a wrong password without revealing whether the email exists.

### Key Entities

- **Account**: email address, credential, creation time.
- **Session**: account reference, expiry.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user completes account creation in under 2 minutes.
- **SC-002**: 95% of returning users see their saved items within 2 seconds of signing in.
- **SC-003**: Wrong-password attempts never reveal account existence.

## Assumptions

- Existing saved-item storage is reused rather than replaced.
- Passwords are stored with a one-way hash; the specification does not choose a library.
