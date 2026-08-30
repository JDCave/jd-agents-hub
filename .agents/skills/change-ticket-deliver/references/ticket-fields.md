# Ticket Fields Reference

Semantics of the ticket header (simple `key: value` lines between `---` fences, keys
alphabetically sorted per the dotagents protocol) and the body sections. The skeleton
lives at `assets/ticket-template.md`; a filled example at `assets/example-ticket.md`.

## Header fields

| Field | Values | Meaning |
| --- | --- | --- |
| `branch` | `(none)` or branch name | Working branch for this ticket; set when work starts |
| `created` | `YYYY-MM-DD` | Date the ticket was recorded |
| `id` | `CHANGE-NNN` | Allocated by `ticket_utils.py next-id` / `new-ticket` |
| `status` | see below | Current lifecycle state — the single source of truth for resuming |
| `tag` | `(none)` or `vX.Y.Z` | Acceptance tag created in the accept step |
| `title` | short text, no colon | One-line summary; colons would break naive `key: value` parsing |
| `type` | `problem` \| `idea` | problem = fix (patch bump); idea = new requirement (minor bump) |
| `updated` | `YYYY-MM-DD` | Touched on every header change |

## Status values

`open` → `in-progress` → `awaiting-acceptance` → `accepted` → `delivered` → `merged`;
`abandoned` is terminal from any pre-acceptance state. See
[lifecycle.md](lifecycle.md) for the full transition table.

## Body sections

- **Description** — what went wrong and the expected behavior (problem), or what the
  user wants to achieve and why (idea)
- **Acceptance criteria** — checklist that defines done; each item independently checkable
- **Verification evidence** — gate commands with exit codes and results, recorded before
  requesting acceptance
- **Progress log** — append-only, one dated line per transition (`- YYYY-MM-DD — from → to; what happened`)
- **Acceptance record** — acceptance decision (accepted/rejected), date, reviewer notes
- **Release record** — version, tag, PR URL, merge date (filled at accept/deliver time)

All ticket content is written in English.
