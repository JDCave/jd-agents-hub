# Upstream provenance and port record

This skill ports the **process** of GitHub spec-kit's spec-driven-development
commands. It does not port the `specify` command-line interface, its integration
layer, or its extension runtime.

## Source

| Item | Value |
|---|---|
| Repository | https://github.com/github/spec-kit |
| Commit pin | `c43849408ac0de2ca6a52f14eaae71449776057b` |
| Commit date | 2026-11-06 |
| Source version | `specify-cli 1.3.3.dev0` |
| License | MIT |

The clone was read-only during authoring; nothing in it was modified.

## Ported files

Command bodies, ported into flat reference files with the gates, caps, ids,
artifact names, and error conditions kept close to the source:

| Upstream path | Ported to | Notes |
|---|---|---|
| `templates/commands/constitution.md` | `references/command-constitution.md` | Semver rules, TODO placeholders, sync impact report, scope guard kept |
| `templates/commands/specify.md` | `references/command-specify.md` | WHAT/WHY rule, 3-marker cap, requirements checklist, question table kept |
| `templates/commands/clarify.md` | `references/command-clarify.md` | 5-question cap, taxonomy, answers written back to the spec kept |
| `templates/commands/plan.md` | `references/command-plan.md` | Constitution Check gate, Phase 0/1 artifacts, re-check kept |
| `templates/commands/checklist.md` | `references/command-checklist.md` | "Unit tests for English" framing, reviewer ownership, CHK ids kept |
| `templates/commands/tasks.md` | `references/command-tasks.md` | Strict task format, story grouping, phases, MVP scope kept |
| `templates/commands/analyze.md` | `references/command-analyze.md` | Read-only rule, CRITICAL/HIGH/MEDIUM/LOW, findings cap kept |
| `templates/commands/implement.md` | `references/command-implement.md` | Checklist gate, phase execution, `[X]` marking kept |
| `templates/commands/converge.md` | `references/command-converge.md` | Append-only contract, gap types, byte-identical rule kept |

Page templates, copied verbatim under `assets/templates/`:

| Upstream path | Ported to |
|---|---|
| `templates/constitution-template.md` | `assets/templates/constitution-template.md` |
| `templates/spec-template.md` | `assets/templates/spec-template.md` |
| `templates/plan-template.md` | `assets/templates/plan-template.md` |
| `templates/tasks-template.md` | `assets/templates/tasks-template.md` |
| `templates/checklist-template.md` | `assets/templates/checklist-template.md` |

The five page templates are byte-for-byte copies of the pinned source except for
line-ending normalization and renderer-token normalization noted in Modifications
item 9. They keep their upstream placeholder conventions, including the
`[ALL_CAPS_IDENTIFIER]` tokens and their template notes; the command references
tell the agent to replace the sample content when filling an artifact.

Process framing was read from `spec-driven.md` and
`docs/reference/agentic-sdd.md`; those documents are not redistributed here. The
skill's `references/mechanisms.md` records the order, the optional gates, and the
cross-cutting rules that the framing describes.

## Modifications

Every change below is deliberate; the gates survive, the platform glue does not.

1. **Script invocations replaced.** Every upstream script placeholder call became
   `python scripts/sdd_workflow.py --action <equivalent> --json`. Paths are
   relative to this skill folder; there is no `.agents/` prefix and no `.specify/`
   script install.
2. **Command handoffs replaced.** Every cross-command placeholder became a plain
   "Next step" sentence naming the matching `references/command-<name>.md` file.
3. **Hook sections replaced.** The per-command `## Pre-Execution Checks` and
   `## Mandatory Post-Execution Hooks` sections became one short pointer to
   `references/mechanisms.md`, which states that extension hooks, presets, the
   `specify` CLI, and integration dispatch are not ported.
4. **Scripts reimplemented, not vendored.** The upstream helper modules were not
   copied. One compact standard-library entry point supplies the six mechanical
   behaviors the commands need: skeleton bootstrap, feature allocation and
   `feature.json` persistence, prerequisite resolution, plan and tasks seeding,
   and template resolution. Flag names, JSON keys, numbering, and error messages
   were kept where practical; the CLI shape is a single `--action` surface rather
   than per-script entry points.
5. **Template resolution simplified.** Upstream composes project overrides, preset
   layers, extension layers, and core templates. This port keeps only project
   override then bundled asset, because presets and extensions are dropped.
6. **Timestamp numbering removed.** Only sequential `NNN` feature numbering is
   ported; the timestamp strategy and its init option are documented as dropped.
7. **Hook-driven branch creation removed.** Upstream's git hook owns branch
   creation. This port leaves branch, commit, and pull-request lifecycle to the
   hub's change-ticket workflow and documents that ownership in the specify
   reference.
8. **README, samples, expected outputs, and tests added.** These are new hub
   artifacts, not upstream content.
9. **Renderer tokens normalized in the page templates.** The upstream
   `__SPECKIT_COMMAND_<NAME>__` tokens became plain step names (for example
   "plan step"), and the spec template's `$ARGUMENTS` became
   `[FEATURE DESCRIPTION]`, so a scaffolded artifact contains no renderer
   placeholders. Nothing else in the templates changed.

## Dropped from upstream

Not ported, by design:

- The `specify` CLI and its subcommands.
- Integration adapters and per-agent rendering of commands.
- The extension system, `.specify/extensions.yml`, hook dispatch, and hook
  conditions.
- Presets and their replace, prepend, append, and wrap composition strategies.
- Bundles, the workflow engine, extension catalogs, and event plumbing.
- The git extension, GitHub issue export, agent-context updates, and selftest.
- Upstream media, screenshots, and documentation trees.

## License notice

MIT License

Copyright (c) GitHub, Inc.

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

## Re-sync policy

Pin the commit, diff the ported file list against a newer upstream release, and
re-run the unit tests and the hub gate after any re-sync. The five page templates
are the most likely to drift; diff them first.
