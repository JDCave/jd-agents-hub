# Rewrite Patterns — Bullet Fixes & Project Templates (zh + en)

Patterns for the optimize workflow. Every rewrite keeps the candidate's real
facts — patterns change expression, never invent evidence. Chinese and
English versions are parallel; pick the row matching the resume's detected
language.

## 1. Bullet rewrite patterns

| # | Pattern | Before (zh) | After (zh) |
|---|---|---|---|
| 1 | Empty → STAR | 参与了项目的开发工作 | 主导 X 模块开发，支撑日均 500+ 次调用，可用性 99.9% |
| 2 | Task → Result | 负责后端接口的实现 | 设计并实现 12 个核心接口，P99 延迟从 800ms 降至 200ms |
| 3 | Vague → Number | 大幅提升了系统性能 | 通过语义缓存（命中率 35%）将 LLM API 成本降低 25% |
| 4 | Weak verb → Ownership | 协助团队完成部署 | 搭建 CI/CD 流水线，部署耗时从 1 小时缩短到 10 分钟 |
| 5 | Learning → Building | 学习了 RAG 相关知识 | 实现混合检索 RAG 链路，问答准确率从 68% 提升至 85% |
| 6 | List → Decision | 使用了 Redis 和 PostgreSQL | 引入 Redis 语义缓存解决重复查询开销，月度 API 成本降 25% |

| # | Pattern | Before (en) | After (en) |
|---|---|---|---|
| 1 | Empty → STAR | Participated in agent development | Led the X module, serving 500+ calls/day at 99.9% availability |
| 2 | Task → Result | Responsible for backend endpoints | Designed 12 core endpoints, cutting P99 latency from 800ms to 200ms |
| 3 | Vague → Number | Greatly improved performance | Added a semantic cache (35% hit rate), cutting LLM API spend 25% |
| 4 | Weak verb → Ownership | Assisted the team with deployment | Built the CI/CD pipeline, shrinking deploys from 1 hour to 10 minutes |
| 5 | Learning → Building | Learned about RAG | Built a hybrid-retrieval RAG chain, raising answer accuracy from 68% to 85% |
| 6 | List → Decision | Used Redis and PostgreSQL | Chose Redis semantic caching to kill duplicate-query cost, −25% monthly API spend |

Rewrite checklist per bullet: ownership verb first → action + tech decision →
numbered outcome. If no number exists, ask the candidate for one; if truly
none, the bullet merges into another or drops.

## 2. Project block template (7 elements)

zh:

```text
【项目名称】                        【YYYY.MM - YYYY.MM】
角色：【独立研究 / 核心开发 / 技术负责人】
技术栈：【语言, 框架, 协议, 存储, 部署】
描述：【2-3 句：什么场景、什么规模、解决什么问题】
职责：
- 【架构/源码理解类，1 条】
- 【核心开发类，2-3 条】
- 【优化决策类，1 条】
成果：
- 【量化成果 1】
- 【量化成果 2】
```

en:

```text
【Project Name】                    【Mon YYYY – Mon YYYY】
Role: 【independent researcher / core developer / tech lead】
Stack: 【languages, frameworks, protocols, storage, deployment】
Summary: 【2-3 sentences: context, scale, problem solved】
Responsibilities:
- 【architecture/source-study item, 1】
- 【core development items, 2-3】
- 【optimization decision, 1】
Results:
- 【quantified result 1】
- 【quantified result 2】
```

## 3. Four project archetypes (pick 2, go deep)

| Archetype | Fits | Core selling points |
|---|---|---|
| 框架源码研究 / framework source study | architecture-leaning roles | framework core internals study (约 4000 行 / ~4,000 lines): execution-loop / memory / registry analysis; deep-dive docs output |
| 企业智能助手 / enterprise assistant | engineering/product roles | channel adapters for multi-platform access; 5+ custom MCP servers; progressive-disclosure skills (system prompt tokens −40%); semantic cache (API cost −25%) |
| MCP Server 集群 / MCP server cluster | infrastructure/protocol roles | 6–8 servers; unified security (auth, schema validation, destructive annotations, audit); stdio + HTTP/SSE dual transport; call accuracy 78%→95% |
| 领域落地 / domain delivery (ops, support) | domain roles | multi-step reasoning auto-diagnosis (30min→5min); memory-accumulated incident knowledge; 200+ concurrent sessions; support cost −35% |

## 4. Skills section skeleton

zh:

```text
• 编程语言：Python（【熟练度】）、【其他】（熟悉）
• AI/LLM：Prompt Engineering、RAG 系统设计、Agent 架构、MCP 协议、Function Calling
• Agent 框架：【框架名】（源码级理解 / 项目实践）
• 模型训练：PyTorch、Transformer 架构、SFT/DPO、LoRA 微调
• 后端与工程：FastAPI、PostgreSQL、Redis、向量数据库、Docker、asyncio、Git
```

en:

```text
• Languages: Python (【level】), 【others】 (proficient)
• AI/LLM: Prompt engineering, RAG system design, agent architecture, MCP protocol, function calling
• Agent frameworks: 【framework】 (source-level understanding / project work)
• Model training: PyTorch, Transformer architecture, SFT/DPO, LoRA fine-tuning
• Backend & engineering: FastAPI, PostgreSQL, Redis, vector database, Docker, asyncio, Git
```

Order lines by target-role emphasis (keyword-tiers.md per-role table).

## 5. Self-section skeleton (3–5 bullets zh / 2–3 lines en)

zh 自我评价:

```text
• 对 AI Agent 系统有深入理解，研读过【框架】源码，掌握执行循环/记忆/注册机制
• 熟悉 MCP 协议，有自主开发 MCP Server 的实践
• 扎实的 Python 基础，熟练 asyncio 异步编程
• 【开源 / 博客 / 文档输出，附链接】
```

en Summary (or omit — see resume-standards.md §6):

```text
AI Agent engineer with source-level framework understanding and shipped
MCP server clusters; cut LLM API cost 25% via semantic caching. 【links】
```

## 6. Full-page assembly order

- zh: 基本信息 → 教育背景 → 技术技能 → 项目经历（最强且最匹配 JD 的放第一）→ 自我评价/个人亮点; one A4 page.
- en: header (name + contact) → Summary (optional) → Skills → Experience
  (strongest JD match first) → Education; one page (two for 10+ years).
- Cut weakest content first, never shrink font.
