# Opening a PR by hand (no gh CLI)

When `gh` is not installed, open the PR on GitHub directly. The ticket file itself is
the PR body — no separate PR-description file is created.

## Steps

1. Push the branch and tag (see [session-example.md](session-example.md)).
2. Open the compare URL (fill in owner/repo and the branch slug):

   `https://github.com/<owner>/<repo>/compare/main...feature/CHANGE-NNN-short-slug`

   GitHub also prints a `pull/new/<branch>` link after every `git push -u`.

3. Title: `[CHANGE-NNN] <short title>` — same title as the ticket header.
4. Body: paste the full content of `tickets/delivered/CHANGE-NNN.md`.
5. Base: `main`.

## Merge mode

- Merge commit (`--merge`) keeps the tagged branch commit reachable from main —
  `git describe main` will find the version tag.
- Squash (`--squash`) leaves the tag on the (soon-deleted) branch commit; harmless
  for version scanning (`git tag --list`), just not reachable from main.

After merging, set the ticket status to `merged` and commit that on main.
