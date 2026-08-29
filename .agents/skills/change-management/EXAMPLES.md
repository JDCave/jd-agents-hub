# Examples

A worked session for the change-management workflow. Commands run from the repo root
(PowerShell 7 or bash; `python` ≥ 3.9).

## Example 1: record and start a problem ticket

```bash
$ python .agents/skills/change-management/scripts/ticket_utils.py new-ticket --type problem --title "audit runner path is wrong"
id: CHANGE-001
file: tickets/CHANGE-001.md
next: fill acceptance criteria, then commit
```

Fill 问题描述 and 验收标准 in `tickets/CHANGE-001.md`, then:

```bash
git add tickets/CHANGE-001.md
git commit -m "ticket: record CHANGE-001 (problem)"
git switch -c feature/CHANGE-001-fix-audit-runner main
```

Update the ticket header (`branch: feature/CHANGE-001-fix-audit-runner`, `status:
in-progress`) and append a 进展日志 line, commit.

## Example 2: verify, then request acceptance

Implement the fix, then run the repo gates and paste the evidence into 验证证据:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py --all
python .agents/skills/skill-tester/scripts/audit_skills.py
```

Tick the acceptance checklist, set `status: awaiting-acceptance`, commit, and present
the checklist + evidence to the user. Do NOT tag or push before acceptance.

## Example 3: acceptance, tag, PR

After the user accepts:

```bash
$ python .agents/skills/change-management/scripts/ticket_utils.py next-version --type problem
type: problem
next_version: v0.1.1

git tag -a v0.1.1 -m "CHANGE-001: audit runner path is wrong"
git push -u origin feature/CHANGE-001-fix-audit-runner
git push origin v0.1.1
gh pr create --base main --title "[CHANGE-001] Fix audit runner path" \
  --body-file tickets/CHANGE-001-pr.md
```

PR body skeleton: [assets/example-pr-body.md](assets/example-pr-body.md);
a fully filled-in ticket: [assets/example-ticket.md](assets/example-ticket.md).
