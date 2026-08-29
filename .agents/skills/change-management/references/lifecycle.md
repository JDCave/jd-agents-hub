# Lifecycle Reference

The status machine and conventions behind the change-management workflow. Commands run
from the repo root (PowerShell 7 or bash).

## Status machine

| From | To | Trigger | Agent actions |
| --- | --- | --- | --- |
| — | `open` | user reports a problem or idea | create ticket from template, commit on `main` |
| `open` | `in-progress` | work starts | create branch, update header, append log line |
| `in-progress` | `awaiting-acceptance` | implementation + gates done | record evidence, tick checklist, present to user |
| `awaiting-acceptance` | `in-progress` | user rejects | record reason in Acceptance record, continue work |
| `awaiting-acceptance` | `accepted` | user accepts | create semver tag, fill Acceptance/Release records |
| `accepted` | `delivered` | tag + branch pushed, PR opened | `gh pr create`, record PR URL |
| `delivered` | `merged` | PR merged | switch to main, pull, final ticket commit |
| any pre-acceptance | `abandoned` | user cancels | record reason, keep the file; no branch/tag cleanup unless asked |

## Ticket id allocation

Numeric max over existing files — lexicographic sorting breaks at the CHANGE-999 →
CHANGE-1000 rollover, so never sort by name. The logic lives in
`scripts/ticket_utils.py`; both commands work from any directory inside the repo:

```bash
python .agents/skills/change-management/scripts/ticket_utils.py next-id            # peek
python .agents/skills/change-management/scripts/ticket_utils.py new-ticket --type idea --title "add dark mode"
```

`new-ticket` allocates the id, copies `assets/ticket-template.md` to
`tickets/CHANGE-NNN.md`, and fills id / type / title / dates; fill description and
acceptance criteria by hand before committing.

## Branch naming

`feature/CHANGE-NNN-short-slug` — 2-4 kebab-case words derived from the title, ASCII
only. One ticket per branch; never mix tickets on a branch.

## Commit message conventions

- Ticket record: `ticket: record CHANGE-NNN (problem)`
- Status moves: `ticket: CHANGE-NNN in-progress → awaiting-acceptance`
- Work commits: normal imperative messages; mention `CHANGE-NNN` when it aids tracing
- Stage ticket/skill files by name — never `git add -A` (the repo carries unrelated
  untracked work)
