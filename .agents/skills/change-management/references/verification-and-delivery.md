# Verification and Delivery Reference

What must pass before acceptance, and what must be true before anything leaves the
machine.

## Verification gates

Run from repo root before requesting acceptance; record command + exit code + result
in 验证证据:

- `python .agents/skills/skill-tester/scripts/skill_gate.py --all` — expect all PASS
  (min quality score 90 per skill)
- `python .agents/skills/skill-tester/scripts/audit_skills.py` — expect overall not
  ERROR

The pre-commit hook (`.githooks/pre-commit`, active via `core.hooksPath`) automatically
gates any staged `.agents/skills/**` change with `--update-registry`, so committing
skill work runs the gate again and refreshes `.agents/skills/registry.json` (leave the
registry file uncommitted unless the user asks). CI (`.github/workflows/skill-gate.yml`)
enforces the same gate on PRs and pushes to main — do not bypass with `--no-verify`.

## Delivery prerequisites

```bash
git remote          # must list an origin
gh auth status      # must be logged in
```

If either fails, do not push. Write `tickets/CHANGE-NNN-pr.md` from
`assets/example-pr-body.md` (title `[CHANGE-NNN] <title>`; body = description +
acceptance checklist + verification evidence + tag), then ask the user to push and
open the PR manually.

## Push and PR

```bash
git push -u origin feature/CHANGE-NNN-short-slug
git push origin v0.1.1
gh pr create --base main --title "[CHANGE-NNN] title" --body-file tickets/CHANGE-NNN-pr.md
```

After merge: `gh pr merge --squash --delete-branch` (or `--merge` to keep the tagged
commit reachable — see [versioning-and-tagging.md](versioning-and-tagging.md)), then
`git switch main`, `git pull`, set `status: merged`, commit the final ticket state on
main.
