# Scoring Rubric — Agent Resume Review

Two layers, one verdict. The **lint** (`scripts/resume_lint.py`) covers the
mechanical checks deterministically; this rubric covers the judgment checks a
reviewer must do by reading. Never report a verdict from the lint score alone.
Chinese and English resumes are both first-class: the lint detects the
language and carries zh/en aliases; the reviewer applies the market-specific
conventions (resume-standards.md §6) on top.

## Verdict thresholds

| Overall | Verdict | Meaning |
|---|---|---|
| ≥ 85 | `ready` | Start sending; per-JD tailoring only |
| 70–84 | `optimize` | Run the optimize workflow (rewrite-patterns.md) |
| < 70 | `rewrite` | Structure/content rebuild needed, not polishing |

## Dimensions (100 pts)

### 1. Content & Impact — 25 pts (lint-assisted)

- Every project bullet follows STAR: background → task → action → result.
- Results carry numbers: 提升 X%, 日均 X 次, X→Y, 覆盖 X 个场景.
- Result-oriented, not task-lists ("解决了什么问题" beats "做了什么").
- Penalty reference: −5 per project with zero quantified results; −3 per
  bullet that only describes participation.

### 2. AI Agent Depth — 25 pts (manual; the differentiator for this role)

Four signals, roughly 6 pts each when present and evidenced:

1. **Source-code understanding** — has read a framework's internals (execution
   loop, memory management, registry patterns), not just called its API.
2. **Protocol understanding** — MCP or equivalent: transport modes, schema
   validation, security annotations; ideally built a server from scratch.
3. **End-to-end ownership** — prompt design → system → deployment → measured
   outcome, all by the candidate.
4. **Open-source / writing** — GitHub contributions, technical blog, published
   docs; links present and checkable.

A resume with none of these is a generic backend resume wearing Agent keywords.

### 3. Keyword & JD Fit — 15 pts (lint-assisted)

- Tier-1 keywords covered (see keyword-tiers.md); each appears ≥ 2 times,
  naturally.
- Against a specific JD: extract its keywords, map each to resume evidence.
  Unmappable JD requirements → listed as gaps, never padded.
- Skills order matches the target role's emphasis.

### 4. Structure & Format — 15 pts (lint-assisted)

- Standard sections in order: 基本信息 → 教育背景 → 技术技能 → 项目经历 →
  自我评价/个人亮点.
- Each project uses the 7-element block (rewrite-patterns.md §2): 名称+周期 /
  角色 / 技术栈 / 描述 / 3–5 职责 / 1–2 量化成果.
- One A4 page (10+ years experience excepted); 2 deep projects beat 5 shallow.

### 5. Credibility & Honesty — 10 pts (manual)

- ≤ 3 mastery (精通) claims, each survivable under probing.
- No learning-claims ("学习了 X 相关知识") standing in for built-claims.
- Timeline has no unexplained gaps; project dates are plausible.
- **Non-negotiable**: every line must survive an interviewer deep-dive. If the
  candidate cannot defend it, it comes out — this overrides all scoring.

### 6. ATS & Delivery — 10 pts (manual)

- Parseable headings, no fancy layout/icons/images; PDF on delivery.
- File named 姓名-岗位-联系方式.pdf.
- Contact info complete: phone, email, GitHub.

## Scorecard contract

The evaluate workflow emits this JSON shape (filled example:
`expected_outputs/score-card-example.json`):

```json
{
  "resume": "path",
  "target_role": "ai-agent-engineer",
  "language": "zh | en | mixed",
  "lint_score": 0.0,
  "dimensions": [
    {"name": "content_impact", "weight": 25, "score": 0,
     "evidence": ["..."], "top_fix": "..."}
  ],
  "overall": 0,
  "verdict": "ready | optimize | rewrite",
  "top_actions": ["..."]
}
```

`overall` = Σ(score × weight) / 100. `top_actions` lists at most 5 fixes,
ordered by score impact. `language` mirrors the lint's detection and decides
which market conventions (resume-standards.md §6–7) apply.
