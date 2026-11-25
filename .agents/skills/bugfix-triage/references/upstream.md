# Upstream provenance and port notes

This skill is a port of the spec-kit bug triage extension. It keeps the process,
the artifacts, and the guardrails; it drops the spec-kit platform.

## Source

- Repository: https://github.com/github/spec-kit
- Commit: `c43849408ac0de2ca6a52f14eaae71449776057b`
- Upstream extension: `extensions/bug/` (`extension.yml` version `1.0.2`,
  requires spec-kit `>=0.9.0`)
- License: MIT, Copyright GitHub, Inc.

## Ported files

| Upstream file | Ported to | Notes |
|---|---|---|
| `extensions/bug/README.md` | `SKILL.md`, `references/assess.md`, `references/fix.md`, `references/test.md` | Stage overview, slug conventions, guardrails |
| `extensions/bug/commands/speckit.bug.assess.md` | `references/assess.md`, `references/url-trust-policy.md`, `assets/report-templates/assessment-template.md` | Process, URL rules, and report schema |
| `extensions/bug/commands/speckit.bug.fix.md` | `references/fix.md`, `assets/report-templates/fix-template.md` | Process, contract handling, report schema |
| `extensions/bug/commands/speckit.bug.test.md` | `references/test.md`, `assets/report-templates/test-template.md` | Checks, verdict judgement, report schema |
| `extensions/bug/extension.yml` | this file | Metadata, version, and license only |

The report sections, metadata fields, slug conventions, verdict vocabulary,
severity vocabulary, URL trust rules, and guardrails are preserved close to
verbatim in substance. The three report templates reproduce the schema code
blocks from the upstream command bodies.

## MIT notice

```
MIT License

Copyright GitHub, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Modifications

1. **Flat references instead of command templates.** The three command bodies
   became `references/assess.md`, `references/fix.md`, and `references/test.md`.
   `$ARGUMENTS` and the frontmatter renderer placeholders are replaced by plain
   instructions.
2. **CLI renderer tokens removed.** `__SPECKIT_COMMAND_BUG_ASSESS__`,
   `__SPECKIT_COMMAND_BUG_FIX__`, `__SPECKIT_COMMAND_BUG_TEST__`, and `{SCRIPT}`
   are replaced by next-step sentences and by
   `python scripts/bug_workflow.py --action <action>` invocations relative to
   this skill folder.
3. **Hooks not implemented.** The upstream `before_bug_*` / `after_bug_*` hook
   sections and the `.specify/extensions.yml` dispatch contract are not ported;
   each stage names the next step directly instead. There is no hook runtime.
4. **Mechanical rules reimplemented.** Slug normalization, path containment,
   unique-suffix selection, template seeding, stage presence, and verdict
   vocabulary checking are implemented once in `scripts/bug_workflow.py` as a
   standard-library command, instead of being described for repeated manual
   reproduction in the command bodies.
5. **URL Trust Record section.** The assessment schema gains an explicit
   **URL Trust Record** section so the upstream requirement to record the URL,
   host, and policy branch has a fixed home in the report.
6. **Robust placeholder handling.** Report templates hold their vocabulary in
   angle-bracket placeholders; the workflow command treats such placeholders as
   "not recorded" so a freshly seeded workspace does not look complete.
7. **`not-run` accepted as a result.** The test schema accepts `not-run` in
   addition to the upstream `verified`, `partial`, and `failed`, matching the
   upstream rule that an unexecutable check is recorded rather than fabricated.

## Dropped

- The `specify` CLI and every `specify extension add`, `specify extension
  disable`, and `specify extension enable` command.
- The extension loader, registry, catalogs, presets, bundles, workflow engine,
  and hook runtime (`.specify/extensions.yml`, `EXTENSION` lifecycle events).
- `{SCRIPT}` script selection, `$ARGUMENTS` rendering, and every
  `__SPECKIT_COMMAND_*__` placeholder.
- Integration adapters and per-agent command rendering (the hub's distribution
  step owns installation for each host).
- spec-kit media, tests, and documentation assets.
- Branch, commit, and pull-request lifecycle (the hub's change-ticket workflow
  owns it).

## Re-sync policy

Re-sync when the upstream bug extension changes: diff the five upstream files
listed above against this port, update the commit pin, re-copy the report
schemas, re-run the skill gate, and re-run
`python -m unittest discover -s tests`. Keep the `.specify/bugs/<slug>/` layout
and the slug handle stable — they are the compatibility contract for existing
bug directories.
