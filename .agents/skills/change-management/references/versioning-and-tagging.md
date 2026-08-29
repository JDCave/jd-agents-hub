# Versioning and Tagging Reference

Semantic versioning for accepted changes; tags are created on the feature branch after
user acceptance, before the PR.

## Next version

```bash
python .agents/skills/change-management/scripts/ticket_utils.py next-version --type problem
```

Rules (implemented in `scripts/ticket_utils.py`):

- First ever tag in the repo → `v0.1.0`
- `problem` ticket → patch bump (`v1.2.3` → `v1.2.4`)
- `idea` ticket → minor bump (`v1.2.3` → `v1.3.0`)
- Major bumps only on explicit user instruction

Always annotated, message referencing the ticket:

```bash
git tag -a v0.1.1 -m "CHANGE-NNN: <title>"
```

## Rework after tagging (pre-merge)

Default: leave the tag on the accepted commit, add new commits, re-run the gates, ask
for acceptance again. Re-point a local tag only on explicit user instruction
(`git tag -fa v0.1.1 -m "..."`) and note it in 发布记录. Never move a tag that has
already been pushed — deleting/re-pushing remote tags is visible history surgery and
requires separate user confirmation each time.

## Squash-merge caveat

The tag points at a branch commit. If the PR is squash-merged, that commit is not on
main's first-parent history, so `git describe main` will not find the tag. This is
expected and harmless here: `git tag --list` (used by the next-version scan) lists all
tags regardless of reachability, and the tag is pushed to origin before the PR, so it
survives `--delete-branch`. If reachable-from-main tags matter, merge with
`gh pr merge --merge` instead of `--squash`.
