# Session Example — per-state command cheat sheet

Compact command sequence for each lifecycle state. Run from the repo root; `NNN` is
the ticket number. Detail: [../EXAMPLES.md](../EXAMPLES.md).

## record (on main) — status: open

```bash
python .agents/skills/change-management/scripts/ticket_utils.py new-ticket --type idea --title "short title"
# fill Description + Acceptance criteria in tickets/CHANGE-NNN.md
git add tickets/CHANGE-NNN.md && git commit -m "ticket: record CHANGE-NNN (idea)"
```

## start — status: in-progress

```bash
git switch -c feature/CHANGE-NNN-short-slug main
# update header (branch/status/updated) + append a Progress log line, commit
```

## verify — still in-progress

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py --all
python .agents/skills/skill-tester/scripts/audit_skills.py
# paste commands + exit codes into Verification evidence
```

## await acceptance — status: awaiting-acceptance

```bash
# tick the Acceptance criteria checklist, commit, present checklist + evidence to the user, STOP
```

## accept & tag — status: accepted

```bash
python .agents/skills/change-management/scripts/ticket_utils.py next-version --type idea
git tag -a v0.1.1 -m "CHANGE-NNN: title"
# fill Acceptance record / Release record, add CHANGELOG.md section, set tag: in header, commit
```

## deliver — status: delivered → merged

```bash
git push -u origin feature/CHANGE-NNN-short-slug && git push origin v0.1.1
gh pr create --base main --title "[CHANGE-NNN] title" --body-file tickets/CHANGE-NNN-pr.md
# after merge: gh pr merge --squash --delete-branch; git switch main; git pull
```
