# Upstream provenance

This skill is a hub-native port of GitHub spec-kit's `assess` extension. The
funnel, stage gates, artifact schemas, slug rules, verdict rules, evidence
labelling, and URL trust policy are preserved in substance. The `specify`
command line installer, extension loader, hooks runtime, presets, catalogs,
bundles, workflow engine, and integration dispatch are not ported.

## Source

- Repository: https://github.com/github/spec-kit
- Extension path: `extensions/assess/` (extension id `assess`, version `1.0.2`)
- Commit pin: `c43849408ac0de2ca6a52f14eaae71449776057b`
- License: MIT, Copyright GitHub, Inc.

## Ported source files

| Upstream file | Ported to |
|---|---|
| `extensions/assess/README.md` | `SKILL.md`, `references/upstream.md`, README funnel description |
| `extensions/assess/commands/speckit.assess.intake.md` | `references/intake.md`, `assets/report-templates/intake-template.md` |
| `extensions/assess/commands/speckit.assess.research.md` | `references/research.md`, `assets/report-templates/research-template.md` |
| `extensions/assess/commands/speckit.assess.define.md` | `references/define.md`, `assets/report-templates/problem-template.md` |
| `extensions/assess/commands/speckit.assess.shape.md` | `references/shape.md`, `assets/report-templates/concept-template.md` |
| `extensions/assess/commands/speckit.assess.decide.md` | `references/decide.md`, `assets/report-templates/decision-template.md` |
| `extensions/assess/extension.yml` (command list, descriptions) | stage list and routing in `SKILL.md` |

## Modifications

1. Command-template tokens were replaced with plain instructions. The
   `__SPECKIT_COMMAND_ASSESS_<STAGE>__` handoffs became sentences naming the next
   stage, and `__SPECKIT_COMMAND_SPECIFY__` became the `spec-driven-development`
   skill.
2. The `$ARGUMENTS` input block and `{SCRIPT}` placeholders were removed. Slug
   normalization, path safety, stage scaffolding, status, precondition checks,
   verdict parsing, and reporting are implemented in one standard-library CLI:
   `scripts/assess_workflow.py` with `init`, `stage`, `status`, `check`, and
   `report` actions.
3. The five artifact schemas were moved from the command bodies into
   `assets/report-templates/` so the `stage` action can copy them once and refuse
   to overwrite without `--force`.
4. Extension lifecycle material was dropped: no hooks, no `specify extension
   add`, no enable/disable instructions, no `.specify/extensions.yml`, no
   generated `SKILL.md` frontmatter conventions.
5. Paths are relative to the skill folder in all instructions. The artifact
   contract (`.specify/assessments/<slug>/`) is kept, and no hub layout is
   assumed.
6. The URL trust policy is consolidated into `references/url-trust-policy.md`
   and referenced from intake and research instead of being repeated verbatim in
   each command body.

## Dropped (not ported)

- The `specify` CLI (`specify extension add assess`, `specify extension
  disable/enable assess`) and all integration/agent dispatch machinery.
- Extension manifest, registry installation, and lifecycle hooks; the upstream
  extension registers no lifecycle hooks of its own, and this port registers
  none either.
- Presets, catalogs, bundles, workflows, and the workflow engine.
- Upstream repository media, docs site links, and installation instructions.
- `$ARGUMENTS` and `{SCRIPT}` renderer placeholders.

## MIT license notice

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
