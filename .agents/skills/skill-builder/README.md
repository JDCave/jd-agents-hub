# skill-builder

Create new agent skills with proper structure, progressive disclosure, and bundled
resources. Derived from [Matt Pocock's write-a-skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill)
(MIT); this repo adds programmatic validation on top.

## Usage

How to run each validator (see `--help` on any script for full parameters):

```bash
# 6-item review checklist (description triggers, <100 lines, no time-sensitive
# info, terminology, examples, reference depth)
python .agents/skills/skill-builder/scripts/skill_review_checklist_runner.py path/to/skill-folder

# Description quality (<=1024 chars, third person, "Use when" trigger)
python scripts/skill_description_validator.py path/to/skill-folder/SKILL.md

# Structure (folder layout, reference depth, no circular refs)
python scripts/skill_structure_validator.py path/to/skill-folder
```

For the full lifecycle gate (checklist + frontmatter + structure + script tests +
quality score >= 90 + security audit), use the repo-root gate:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>
```

## Example session

"Write a skill that validates CSV files" → the skill gathers requirements
(columns? delimiter? error output format?), drafts SKILL.md under 100 lines with a
Quick start example, then runs the gate and walks the improvement_roadmap until it
passes.

## References

- [description_design_patterns.md](references/description_design_patterns.md) — trigger writing
- [progressive_disclosure_principles.md](references/progressive_disclosure_principles.md) — what goes in SKILL.md vs references/
- [quality_gates_for_skills.md](references/quality_gates_for_skills.md) — why each gate exists
- [companion_tooling.md](references/companion_tooling.md) — validator catalogue
