---
name: skill-builder
version: "1.1.0"
description: Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, build, or author a new skill.
when_to_use: Authoring or substantially rewriting any skill; drafting SKILL.md; deciding what goes in SKILL.md vs references/ and scripts/.
license: MIT
metadata:
  derived_from: "https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill"
  original_author: "Matt Pocock (@mattpocock)"
  original_license: MIT
  voice: "Matt Pocock — direct, concrete, imperative, example-driven"
  version: 1.1.0
---

# Writing Skills

> Derived from [Matt Pocock's write-a-skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill) (MIT), with this repo's validation tools layered on top.

## Quick start

Draft SKILL.md from the template below, then gate it:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py path/to/skill-folder
```

Apply the top `improvement_roadmap` item from the gate output and re-run until PASS.

## Process

1. **Gather requirements** - What task/domain? Which use cases? Scripts needed or instructions only? Reference materials?
2. **Draft the skill** - SKILL.md with concise instructions; reference files if content exceeds 500 lines; utility scripts if deterministic operations needed.
3. **Review with user** - Does this cover your use cases? Anything missing or unclear? Should any section be more/less detailed?

## SKILL.md Template

```
skill-name/
├── SKILL.md           # frontmatter + Quick start + Workflows (required)
├── REFERENCE.md       # detailed docs (if needed)
├── examples.md        # usage examples (if needed)
└── scripts/           # utility scripts (if needed)
```

SKILL.md body: YAML frontmatter (`name`, `description` with "Use when"
trigger), `# Skill Name`, `## Quick start` with a minimal working example,
`## Workflows` for step-by-step processes, and links to REFERENCE.md for
advanced features.

## Description Requirements

The description is **the only thing your agent sees** when deciding which skill to load. Give your agent just enough info to know (1) what capability this skill provides and (2) when/why to trigger it.

**Format**: max 1024 chars, third person, first sentence says what it does, second sentence is "Use when [specific triggers]".

**Good**: `Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when user mentions PDFs, forms, or document extraction.`

**Bad**: `Helps with documents.` — no way to distinguish this from other document skills.

More patterns: [references/description_design_patterns.md](references/description_design_patterns.md).

## When to Add Scripts

Add utility scripts when the operation is deterministic, the same code would be generated repeatedly, or errors need explicit handling. Scripts save tokens and improve reliability vs generated code. Split files when SKILL.md exceeds 100 lines, content has distinct domains, or advanced features are rarely needed.

## Review Checklist

After drafting, verify:

- [ ] Description includes triggers ("Use when...")
- [ ] SKILL.md under 100 lines
- [ ] No time-sensitive info
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] References one level deep

## Troubleshooting

Common gate failures and their fixes: [references/troubleshooting.md](references/troubleshooting.md). Usage patterns and worked sessions: [examples.md](examples.md).

## Gate and Optimize Loop

Run all 6 review-checklist items programmatically, then the full lifecycle gate:

```bash
python .agents/skills/skill-builder/scripts/skill_review_checklist_runner.py path/to/skill-folder
python .agents/skills/skill-tester/scripts/skill_gate.py path/to/skill-folder   # + structure, script tests, score >= 90, security
```

If the gate fails, apply the top item from the quality scorer's `improvement_roadmap` and re-run until it passes. Validator catalogue: [references/companion_tooling.md](references/companion_tooling.md).
