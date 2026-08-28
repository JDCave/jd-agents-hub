# Companion Tooling

Validation tools layered on top of Matt's write-a-skill. Use these when authoring a new skill in this repo.

## Validation Tools (stdlib Python)

| Tool | Purpose | Run before |
|---|---|---|
| `scripts/skill_description_validator.py` | Validates description: ≤1024 chars, third person, "Use when" trigger, action verb in first sentence | First draft of SKILL.md |
| `scripts/skill_structure_validator.py` | Validates folder structure: SKILL.md present, ≤100 lines, references one level deep, no circular refs | Pre-commit |
| `scripts/skill_review_checklist_runner.py` | Runs all 6 review-checklist items from Matt's write-a-skill against a skill folder | Final check before PR |

All three tools:
- Stdlib-only (no external dependencies)
- Run with embedded sample if no path provided
- Output text or JSON (`--output json`)
- Exit code: 0 if PASS, 1 if FAIL/WARN

## The Skill Gate (repo root)

All of the tools above (plus frontmatter, naming, structure, script tests, quality scoring ≥ 90, and a security audit) are chained by the repo-root gate:

```bash
python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/<name>   # one skill
python .agents/skills/skill-tester/scripts/skill_gate.py --all                  # every skill
```

Single exit code: 0 = pass, 1 = blocked. Pre-commit and CI call this — see [doc/skill-lifecycle-management.md](../../../../../doc/skill-lifecycle-management.md) for the full lifecycle.

## Interrogation Questions (from Matt's review-with-user phase)

**Opening question:** "What capability does this skill provide, and what's the trigger phrase that distinguishes it from existing skills?"

**Six forcing questions** (matches the review checklist):
1. What's the description? Is it ≤1024 chars + third person + has "Use when ..."?
2. Is SKILL.md under 100 lines? If not, where will the split land (REFERENCE.md / EXAMPLES.md / references/)?
3. Are there time-sensitive claims (dates, "as of YYYY")?
4. Is terminology consistent — same word for the same concept throughout?
5. Concrete examples — at least 1 code block, ideally good/bad contrast?
6. References one level deep, no circular refs?

## Why Wrap Matt's Original

Matt's write-a-skill is a tight, principled, ~93-line skill — perfect as-is for individual authoring sessions. The wrapper layers add two things this repo benefits from at scale:

1. **Programmatic enforcement** of Matt's review checklist (the validation tools) — prevents human review-checklist drift across many skills.
2. **Citation-backed references** — Matt links to his own materials; the wrapper adds authoritative external sources per reference (Anthropic skill docs + community precedent + research) for newcomers learning the pattern.

This is the [hybrid voice approach](../SKILL.md): Matt's words for the principles, our additions for the tooling.

## Attribution

Original: [matt-pocock/skills/skills/productivity/write-a-skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill) (MIT).

---

**Source authorities (non-exhaustive):**

- **Matt Pocock — write-a-skill** (https://github.com/mattpocock/skills/, MIT, 2024) — the upstream source
- **Anthropic — Skills documentation** (https://docs.claude.com/en/docs/agents/skills) — official guidance on skill structure
- **Anthropic Engineering Blog — Skills patterns** (continuously updated) — patterns for skill authoring
- **Karpathy, A. — "Software 3.0" + LLM coding pitfalls** (X.com posts 2024-2025) — discipline reference applied throughout this repo's karpathy-coder skill
- **Pareto principle applied to documentation** — concise = trustworthy; 80% of value in 20% of words
- **Hyrum's Law** as applied to skill descriptions — once a description shape is observed, downstream agents depend on it
- **Conway's Law as applied to skill libraries** — skill organization mirrors team responsibilities; progressive disclosure mirrors information needs across team boundaries
