# Examples

A worked session for the change-ticket-deliver workflow. Commands run from the repo root
(PowerShell 7 or bash; `python` ≥ 3.9).

## Example 1: record and start a problem ticket

```bash
$ python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py new-ticket --type problem --title "audit runner path is wrong"
id: CHANGE-001
file: tickets/backlog/CHANGE-001.md
next: fill acceptance criteria, then commit
```

Fill Description and Acceptance criteria in `tickets/backlog/CHANGE-001.md`, then:

```bash
git add tickets/backlog/CHANGE-001.md
git commit -m "ticket: record CHANGE-001 (problem)"
git switch -c feature/CHANGE-001-fix-audit-runner main
```

Update the ticket header (`branch: feature/CHANGE-001-fix-audit-runner`, `status:
in-progress`) and append a Progress log line, commit.

## Example 2: verify, then request acceptance

Implement the fix, then run the repo gates and paste the evidence into Verification
evidence:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py --all
python .agents/skills/skill-tester/scripts/audit_skills.py
```

Tick the acceptance checklist, set `status: awaiting-acceptance`, commit, and present
the checklist + evidence to the user. Do NOT tag or push before acceptance.

## Example 3: acceptance, tag, PR

After the user accepts:

```bash
$ python .agents/skills/change-ticket-deliver/scripts/ticket_utils.py next-version --type problem
type: problem
next_version: v0.1.1

git tag -a v0.1.1 -m "CHANGE-001: audit runner path is wrong"
git mv tickets/backlog/CHANGE-001.md tickets/delivered/
git push -u origin feature/CHANGE-001-fix-audit-runner
git push origin v0.1.1
gh pr create --base main --title "[CHANGE-001] Fix audit runner path" \
  --body-file tickets/delivered/CHANGE-001.md
```

The ticket file itself is the PR body. Opening the PR by hand instead (no gh CLI):
[examples/pr-example.md](examples/pr-example.md); a fully filled-in ticket:
[assets/example-ticket.md](assets/example-ticket.md).
