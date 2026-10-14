# Worked Example — Weak Resume to Ready

A condensed evaluate → optimize session using the bundled zh samples. The en
samples follow the identical path with the en pattern column
(`sample-resume-weak-en.md` 43.6 → `sample-resume-strong-en.md` 100).

## Step 1: lint the resume

```bash
$ python scripts/resume_lint.py assets/sample-resume-weak.md
Language: zh
Lint score: 45.7/100

Components:
  sections            20 / 20
  quantification     0.0 / 25
  weak_verbs           0 / 15
  keywords          10.7 / 25
  mastery_claims       5 / 5
  length              10 / 10

Findings:
  [HIGH  ] quantification: only 0% of 8 bullets carry a number (target ≥ 60%)
  [HIGH  ] weak_verbs: weak verbs present: 参与, 协助, 参加, 帮助
  [HIGH  ] keywords: tier-1 missing: function calling, asyncio
  [MEDIUM] keywords: tier-2 missing: mcp, langchain, docker, ...
```

## Step 2: rubric scorecard (judgment layer)

Full card: `expected_outputs/score-card-example.json`. Summary:

| Dimension | Weight | Score | Key evidence |
|---|---|---|---|
| content_impact | 25 | 15 | task-list bullets, zero numbers |
| agent_depth | 25 | 30 | API usage only; no source-code / protocol / end-to-end |
| keyword_jd_fit | 15 | 40 | tier-1 half covered, tier-2 empty |
| structure_format | 15 | 70 | sections fine; no 7-element project blocks |
| credibility | 10 | 60 | learning-claims standing in for built-claims |
| ats_delivery | 10 | 70 | headings parse; delivery format unknown |

Overall 41 → verdict `rewrite`.

## Step 3: rewrite with patterns

Pattern applications (rewrite-patterns.md §1):

| Pattern | Before | After |
|---|---|---|
| Empty → STAR | 参与了项目的需求分析和方案讨论 | 主导需求分析,拆解 3 个核心场景,定义问答准确率 ≥85% 的验收标准 |
| Learning → Building | 学习了 Prompt 和 RAG 相关知识 | 实现混合检索 RAG 链路,问答准确率从 68% 提升至 85% |
| Weak → Ownership | 协助团队完成系统的测试和部署 | 搭建自动化部署流水线,发布耗时从 1 小时降至 10 分钟 |

Then rebuilt the project block with the 7-element template (§2) and picked the
企业智能助手 archetype (§3) to add Agent depth. Result lives in
`assets/sample-resume-strong.md`.

## Step 4: re-lint proves the delta

```bash
$ python scripts/resume_lint.py assets/sample-resume-strong.md
Lint score: 100.0/100
Findings: none — mechanical checks all clean.
```

45.7 → 100 with findings cleared; the rubric layer then confirms depth and
credibility before the verdict moves to `ready`.
