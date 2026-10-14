# agent-resume-review

Evaluate and optimize resumes for AI Agent engineering roles, in both Chinese
and English job markets (STAR-quantified bullets, ownership verbs, keyword
tiers, page limits, ATS-friendly delivery — with per-market conventions for
sections, photos, proficiency wording, and file naming).

## Design

Two layers, one verdict:

1. **Deterministic lint** — `scripts/resume_lint.py` detects the resume
   language (zh / en / mixed), then scores the mechanical rules: required
   sections, contact info, quantified-bullet ratio, weak verbs
   (参与/协助/帮助 and participated/assisted/helped), AI Agent keyword tiers
   (with cross-language synonym groups), mastery claims (精通 / expert), and
   one-page length. Stdlib only; UTF-8 and GBK input.
2. **Judgment rubric** — `references/scoring-rubric.md` defines six dimensions
   (content impact, Agent depth, keyword/JD fit, structure, credibility, ATS
   delivery) a reviewer scores by reading. The lint never replaces this layer.

The optimize workflow maps findings to the zh/en rewrite patterns in
`references/rewrite-patterns.md` and re-lints to prove the improvement.

## Usage

```bash
python scripts/resume_lint.py --help
python scripts/resume_lint.py                                  # bundled weak sample (zh)
python scripts/resume_lint.py                                  # pass any zh or en resume
python scripts/resume_lint.py my-resume.md                     # text report
python scripts/resume_lint.py my-resume.md --json              # machine-readable
python scripts/resume_lint.py my-resume.md --min-score 85      # gate mode, exit 1 below
python -m unittest discover tests                              # regression tests
```

## Example

`assets/sample-resume-weak.md` lints at 45.7 with four findings;
`assets/sample-resume-strong.md` — the same candidate rewritten with the
patterns — lints at 100 with none. The English pair behaves the same
(`sample-resume-weak-en.md` 43.6 → `sample-resume-strong-en.md` 100). The
full worked session (lint → scorecard → rewrites → re-lint) is in
[examples.md](examples.md), and the expected lint JSON for every asset is in
`expected_outputs/`.

## Layout

| Path | Purpose |
|---|---|
| `SKILL.md` | Workflows: evaluate, optimize, verify |
| `scripts/resume_lint.py` | Deterministic bilingual lint CLI |
| `references/` | Rubric, standards (zh/en), keyword tiers, rewrite patterns (zh/en) |
| `assets/` | zh + en weak/strong resume samples, zh + en JD samples |
| `expected_outputs/` | Real lint JSON (zh + en) + filled scorecard |
| `tests/` | Unit tests for the lint rules |
