# Verification and Delivery Reference

What must pass before acceptance, and what must be true before anything leaves the
machine.

## Verification gates

Run from repo root before requesting acceptance; record command + exit code + result
in Verification evidence:

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

If either fails, do not push. Open the PR manually on GitHub (guide:
[../examples/pr-example.md](../examples/pr-example.md)) — title
`[CHANGE-NNN] <short title>`, body = the delivered ticket file's content. The ticket
itself is the PR body; no separate PR-description file is created.

## Push, move, and PR

```bash
git mv tickets/backlog/CHANGE-NNN.md tickets/delivered/
git push -u origin feature/CHANGE-NNN-short-slug
git push origin v0.1.1
gh pr create --base main --title "[CHANGE-NNN] title" --body-file tickets/delivered/CHANGE-NNN.md
```

After merge: `gh pr merge --squash --delete-branch` (or `--merge` to keep the tagged
commit reachable — see [versioning-and-tagging.md](versioning-and-tagging.md)), then
`git switch main`, `git pull`, set `status: merged`, commit the final ticket state on
main.
