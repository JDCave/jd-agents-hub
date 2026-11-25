# Feature Request: Add user authentication

Users need to sign in before they can view their saved items. Today the project has
no account model, so saved items disappear when a browser session ends.

## Ask

- A new user can create an account with an email address and a password.
- A returning user can sign in and see their saved items.
- A signed-in session lasts 30 days on a trusted device.

## Constraints

- The flow must work without client-side scripting.
- Out of scope: social sign-in, multi-factor authentication, account deletion.
- The specification is WHAT and WHY only; no framework or storage choice is made here.
