# Examples

## Example 1: gate a newly authored skill

```bash
$ python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/my-new-skill

[PASS] my-new-skill  (quality 92.0/90)
    [PASS] frontmatter
    [PASS] checklist
    [PASS] structure
    [PASS] scripts — PASS
    [PASS] quality — score 92.0 (A)
    [PASS] security — PASS
    [PASS] name_shadow
```

## Example 2: gate failure and the optimize loop

```bash
$ python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/my-new-skill

[FAIL] my-new-skill  (quality 74.0/90)
    [PASS] frontmatter
    [FAIL] checklist — failed: 1. Description includes triggers
    ...
```

Fix: apply the top `improvement_roadmap` item (visible with `--json`),
here — rewrite the description to "… Use when [specific triggers]". Re-run
the gate. Repeat until PASS. Never report a partial pass.

## Example 3: writing a description that triggers correctly

Good:

```
Extract text and tables from PDF files, fill forms, merge documents. Use when
working with PDF files or when user mentions PDFs, forms, or document extraction.
```

Bad:

```
Helps with documents.
```

The bad example gives the agent no way to distinguish this skill from other
document skills. See [references/description_design_patterns.md](references/description_design_patterns.md).
