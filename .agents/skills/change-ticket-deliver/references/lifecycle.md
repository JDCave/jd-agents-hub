# Lifecycle Reference

The status machine and conventions behind the change-ticket-deliver workflow. Commands run
from the repo root (PowerShell 7 or bash).

## Status machine

| From | To | Trigger | Agent actions |
| --- | --- | --- | --- |
| — | `open` | user reports a problem or idea | create ticket from template, commit on `main` |
| `open` | `in-progress` | work starts | create branch, update header, append log line |
| `in-progress` | `awaiting-acceptance` | implementation + gates done | record evidence, tick checklist, present to user |
| `awaiting-acceptance` | `in-progress` | user rejects | record reason in Acceptance record, continue work |
| `awaiting-acceptance` | `accepted` | user accepts | create semver tag, fill Acceptance/Release records |
| `accepted` | `delivered` | tag + branch pushed, PR opened | `git mv` ticket backlog → delivered, `gh pr create`, record PR URL |
| `delivered` | `merged` | PR merged | switch to main, pull, final ticket commit |
| any pre-acceptance | `abandoned` | user cancels | record reason, keep the file; no branch/tag cleanup unless asked |

## Ticket id allocation and layout

Tickets live in two directories: `tickets/backlog/` (open, in-progress,
awaiting-acceptance, accepted) and `tickets/delivered/` (delivered, merged) — the
ticket moves to `delivered/` at the accept → deliver transition. Id allocation takes
the numeric max over BOTH directories, so ids are never reused after a move.
Lexicographic sorting breaks at the CHANGE-999 → CHANGE-1000 rollover, so never sort
by name. The logic lives in `scripts/ticket_utils.py`; commands work from any
directory inside the repo:

```bash
python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py next-id            # peek
python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py new-ticket --type idea --title "add dark mode"
```

`new-ticket` allocates the id, copies `assets/ticket-template.md` to
`tickets/backlog/CHANGE-NNN.md`, and fills id / type / title / dates; fill description
and acceptance criteria by hand before committing. Keep `tickets/backlog/.gitkeep`
so the directory survives on fresh clones.

## Branch naming

`feature/CHANGE-NNN-short-slug` — 2-4 kebab-case words derived from the title, ASCII
only. One ticket per branch; never mix tickets on a branch.

## Commit message conventions

- Ticket record: `ticket: record CHANGE-NNN (problem)`
- Status moves: `ticket: CHANGE-NNN in-progress → awaiting-acceptance`
- Work commits: normal imperative messages; mention `CHANGE-NNN` when it aids tracing
- Stage ticket/skill files by name — never `git add -A` (the repo carries unrelated
  untracked work)
