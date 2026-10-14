---
name: "agent-resume-review"
version: "1.1.0"
license: MIT
description: "Evaluate and optimize resumes for AI Agent engineering roles in both Chinese and English job markets: run a deterministic bilingual lint (sections, quantified bullets, weak verbs, keyword tiers, mastery claims, one-page length), score six judgment dimensions (impact, Agent depth, JD fit, structure, credibility, ATS delivery), then rewrite bullets with STAR/ownership-verb/keyword patterns until the verdict is ready. Use when the user asks to review, score, polish, or optimize a resume or CV (中文或英文简历), mentions an AI Agent or LLM job application, or wants resume bullets rewritten with quantified results."
when_to_use: "Reviewing, scoring, or rewriting a zh or en resume; preparing an AI Agent role application; matching a resume against a JD."
---

# Agent Resume Review

Two-layer evaluation and rewrite for AI Agent engineer resumes, zh and en. Layer 1 is deterministic: `scripts/resume_lint.py` detects the resume language, then scores sections, quantified bullets, weak verbs (参与/协助/participated/assisted), keyword tiers, mastery claims (精通/expert), and length. Layer 2 is judgment: the rubric scores architecture understanding, implementation depth, performance claims, and credibility — things a script cannot see. The optimize workflow rewrites with patterns for the detected language, and a re-lint proves the delta.

## Quick Start

```bash
# Demo mode: lint the bundled weak sample (no args needed)
python .agents/skills/agent-resume-review/scripts/resume_lint.py

# Lint a real resume; --json for machine-readable output
python .agents/skills/agent-resume-review/scripts/resume_lint.py path/to/resume.md --json
```

## When to Use

- The user asks to 评估 / 优化 / 打分 a resume (zh or en), or is applying to AI Agent / LLM roles
- A resume must be matched against a specific JD (keyword mapping, zh or en JD)
- Bullets need quantified STAR rewrites before sending

## Workflows

### 1. Evaluate (score)

1. Run the lint (Quick Start) and collect `language`, `score`, `components`, `findings`.
2. Read `references/scoring-rubric.md`; score the six judgment dimensions by reading the resume. Quote the exact line as evidence per dimension. Apply the market conventions for the detected language (`references/resume-standards.md` §6: section order, photo/age rules, self-section style).
3. Emit the scorecard JSON (contract and filled example: `expected_outputs/score-card-example.json`): `overall` = Σ(score × weight) / 100; verdict `ready` ≥ 85, `optimize` 70–84, `rewrite` < 70. Never report a verdict from the lint score alone.

### 2. Optimize (rewrite)

1. Map each finding and scorecard action to a pattern in `references/rewrite-patterns.md` — zh and en tables side by side (§1), 7-element project block (§2), archetypes (§3), skills/self-section skeletons (§4–5). Pick the column matching the detected language.
2. Rewrite each bullet: ownership verb first (主导/led) → action + technical decision → numbered outcome (API cost −25%). Patterns change expression, never facts — ask the candidate for missing numbers instead of inventing them.
3. Tune keywords per target role (`references/keyword-tiers.md`); unmappable JD keywords stay listed as gaps.
4. Re-lint and compare: the score must rise and the targeted findings must clear. Reference before/after pairs: zh `assets/sample-resume-weak.md` → `sample-resume-strong.md` (lint 45.7 → 100); en `sample-resume-weak-en.md` → `sample-resume-strong-en.md` (43.6 → 100).

### 3. Verify before sending

Run the pre-send checklist (`references/resume-standards.md` §8): one page, PDF named per market convention (姓名-岗位-联系方式.pdf / FirstName-LastName-Role.pdf), standard headings, every line defensible in an interview.

## Verification

```bash
python .agents/skills/agent-resume-review/scripts/resume_lint.py resume.md --min-score 85  # must exit 0
python -m unittest discover .agents/skills/agent-resume-review/tests                      # regression
```

## Limitations

- The lint is mechanical and can be gamed; rubric dimension 5 (credibility) is the backstop — every line must survive an interview probe.
- zh and en markets are both covered (sections, verbs, proficiency, naming, layout conventions); other regional variants (jp, de, ...) fall back to the en rules and need reviewer judgment.
- Cannot verify facts, links, or timeline truth — flag suspicious claims for the candidate to confirm.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Chinese output shows mojibake | Script already re-encodes to UTF-8; set `PYTHONUTF8=1` in the calling console |
| Resume is GBK-encoded | Handled automatically (UTF-8 → GBK read fallback) |
| Language misdetected | Detection uses CJK share of letters (zh > 0.25, en < 0.1); treat `mixed` as reviewer-decided |
| Keyword flagged missing but present as a synonym | Extend the synonym groups in `TIER1_KEYWORDS` / `TIER2_KEYWORDS` |
| JD keyword has no resume evidence | Report it as a gap; never pad keywords (rubric dimension 5) |

## References

- [references/scoring-rubric.md](references/scoring-rubric.md) — verdict thresholds, six dimensions, scorecard JSON contract
- [references/resume-standards.md](references/resume-standards.md) — STAR, six golden rules, verb tiers, zh/en market conventions, pre-send checklist
- [references/keyword-tiers.md](references/keyword-tiers.md) — four keyword tiers, per-role tuning, JD matching method
- [references/rewrite-patterns.md](references/rewrite-patterns.md) — zh/en bullet rewrite tables, project block template, four archetypes
- Worked session: [examples.md](examples.md); zh+en samples in `assets/`, expected lint output in `expected_outputs/`
