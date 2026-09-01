---
name: "change-ticket-deliver"
version: "1.0.0"
license: MIT
description: "Manages the full change lifecycle for reported problems and proposed ideas — record each as a numbered markdown ticket (tickets/backlog/CHANGE-001.md), create a feature branch, verify with the repo skill gate, tag accepted changes with semantic versions, and open PRs to main. Use when the user reports a problem or bug, proposes an idea or new requirement, or mentions a change ticket, CHANGE id, version tag, or asks to resume, accept, or deliver a change."
when_to_use: "Recording a reported problem or proposed idea as a ticket; starting, verifying, tagging, or PR-ing a change; resuming an in-flight change ticket."
---

# Change Ticket Deliver

Record problems (bugs hit while using agents/skills) and ideas (new requirements) as numbered markdown tickets in `tickets/`, then drive each through branch → verify → user acceptance → semver tag → PR to main. One ticket per branch — never mix tickets.

## Quick Start

```bash
python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py new-ticket --type problem --title "fix login flow"
git switch -c feature/CHANGE-001-short-slug main
```

## When to Use

- User reports a bug, error, or friction while using agents/skills → type `problem`; user proposes an idea or new requirement → type `idea`
- User mentions a CHANGE id / ticket / version tag, or asks to resume or deliver a change

## Harness mapping

| Harness subsystem | Here |
| --- | --- |
| Instructions | This file + `assets/ticket-template.md` |
| State | Ticket header (`status`, `branch`, `tag`) + 进展日志 + git history |
| Verification | skill gate + audit; evidence pasted into the ticket |
| Scope | Acceptance checklist = definition of done; no work outside it |
| Session lifecycle | Resume by reading the newest non-merged ticket + `git log` |

## Workflows

### 1. Record — `status: open`

On `main`, scaffold the ticket (allocates the next id from the existing files), fill description and acceptance criteria, then stage ONLY this file:

```bash
python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py new-ticket --type problem --title "short title"
git add tickets/backlog/CHANGE-NNN.md
git commit -m "ticket: record CHANGE-NNN (problem)"
```

Never `git add -A` — the repo carries unrelated untracked work.

### 2. Start — `status: in-progress`

`git switch -c feature/CHANGE-NNN-short-slug main`, then update the ticket header (`branch`, `status`, `updated`), append a Progress log line, commit.

### 3. Work & verify — still `in-progress`

Implement only what the acceptance checklist covers. Before claiming done, run the gates in [Verification](#verification) and record command + exit code in Verification evidence.

### 4. Await acceptance — `status: awaiting-acceptance`

Tick the checklist, commit, present checklist + verification evidence to the user, then STOP — no tag, no push before acceptance. On rejection: record why in Acceptance record, set `status: in-progress`, continue.
### 5. Accept & tag — `status: accepted`

Only after explicit user acceptance. Example: `python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py next-version --type problem` prints the next tag (first tag → `v0.1.0`; `problem` → patch; `idea` → minor). Annotated tag on the branch: `git tag -a v0.1.1 -m "CHANGE-NNN: title"`. Fill Acceptance record and Release record, set `tag:` in the header, add a `CHANGELOG.md` section for the new version (one bullet referencing CHANGE-NNN), commit.

### 6. Deliver — `status: delivered`

Prerequisites: `git remote` shows origin and `gh auth status` succeeds — otherwise open the PR manually on GitHub (title `[CHANGE-NNN] title`, body = the ticket file itself; see `examples/pr-example.md`).

```bash
git mv tickets/backlog/CHANGE-NNN.md tickets/delivered/
git push -u origin feature/CHANGE-NNN-short-slug
git push origin v0.1.1
gh pr create --base main --title "[CHANGE-NNN] title" --body-file tickets/delivered/CHANGE-NNN.md
```

After merge: `gh pr merge --squash --delete-branch`, `git switch main`, `git pull`, set `status: merged`, commit on main.## Verification

Usage: run both gates from repo root before requesting acceptance; record command + exit code + result in 验证证据.

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py --all
python .agents/skills/skill-tester/scripts/audit_skills.py
```

## Resuming a session

1. List `tickets/backlog/` and `tickets/delivered/` headers; find the newest ticket not `merged`/`abandoned`.
2. `git log --oneline -10` + `git status` to reconstruct state.
3. Continue from that status; append a Progress log line on every transition.

Status machine: `open → in-progress → awaiting-acceptance → accepted → delivered → merged` (rejection → `in-progress`; abandon allowed pre-acceptance).

## Examples

Example: a full session from ticket to PR lives in [examples.md](examples.md); a compact per-state command cheat sheet in [examples/session-example.md](examples/session-example.md); a filled-in ticket in `assets/example-ticket.md`.

## References

- [references/lifecycle.md](references/lifecycle.md) — status machine, id allocation, branch/commit conventions; [references/ticket-fields.md](references/ticket-fields.md) — header fields and body sections
- [references/versioning-and-tagging.md](references/versioning-and-tagging.md) — semver rules, tag rework, squash caveat; [references/verification-and-delivery.md](references/verification-and-delivery.md) — gates, pre-commit/CI wiring, PR prerequisites
