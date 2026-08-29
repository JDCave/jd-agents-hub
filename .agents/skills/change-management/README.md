# change-management

Ticket-driven change workflow for this repo: every reported **problem** (bug hit while
using agents/skills) or **idea** (new requirement) becomes a numbered markdown ticket
that drives a branch → verify → acceptance → tag → PR lifecycle.

## Quick usage

From the repo root:

```bash
# 1. record a ticket (allocates tickets/CHANGE-NNN.md from the template)
python .agents/skills/change-management/scripts/ticket_utils.py new-ticket --type idea --title "add dark mode"
# fill in description + acceptance criteria, then:
git add tickets/CHANGE-001.md; git commit -m "ticket: record CHANGE-001 (idea)"

# 2. start work on a dedicated branch
git switch -c feature/CHANGE-001-dark-mode main

# 3. before acceptance: next semantic version for the eventual tag
python .agents/skills/change-management/scripts/ticket_utils.py next-version --type idea
```

More subcommand options: `--json` on any command for machine-readable output;
`python .agents/skills/change-management/scripts/ticket_utils.py --help`.
Worked sessions from ticket to PR: [EXAMPLES.md](EXAMPLES.md).

## Lifecycle

`open → in-progress → awaiting-acceptance → accepted → delivered → merged`
(rejection returns to `in-progress`; a ticket may be abandoned before acceptance).
Full transition table, tagging rules, and edge cases: [references/lifecycle.md](references/lifecycle.md).

## Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Workflow instructions for the agent (authoritative) |
| `scripts/ticket_utils.py` | Deterministic helpers: `new-ticket`, `next-id`, `next-version` |
| `assets/ticket-template.md` | Ticket skeleton copied for every new ticket |
| `assets/example-ticket.md` | A fully filled-in example ticket |
| `assets/example-pr-body.md` | PR body example for the deliver step |
| `examples/session-example.md` | Per-state command cheat sheet |
| `expected_outputs/*.json` | Documented `--json` output shapes of the helpers |
| `tests/test_ticket_utils.py` | Unit tests (`python -m unittest discover -s tests`) |
| `references/*.md` | Lifecycle, ticket fields, versioning, verification/delivery |

The workflow implements the harness-engineering model (doc/harness-engineering.md):
the ticket file is State, its acceptance checklist is Scope, the repo skill gate is
Verification, and resuming means reading the newest non-merged ticket.
