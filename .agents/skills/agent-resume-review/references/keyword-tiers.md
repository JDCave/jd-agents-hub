# Keyword Tiers & Per-Role Tuning

Keyword lists the lint checks (tier-1/2) plus tier-3/4 for the reviewer's
judgment, and how to retune a resume per target role. Tech keywords are
English terms in both markets — a zh resume writes them inline (Python、MCP),
an en resume uses them throughout; coverage rules are identical.

## Tier 1 — must include (lint-checked, synonym groups)

python · agent · llm / 大语言模型 / 大模型 · prompt · rag / 检索增强 ·
function calling / tool calling / 函数调用 · asyncio / 异步 / async

## Tier 2 — strongly recommended (lint-checked, synonym groups)

mcp / model context protocol · langchain / langgraph · nanobot ·
向量数据库 / milvus / faiss / weaviate / qdrant / vector database ·
transformer · fastapi · docker · git

## Tier 3 — bonus

多 Agent 编排 / multi-agent orchestration · SFT / RLHF / DPO · LoRA · PyTorch ·
系统设计 / system design · CI/CD · Kubernetes / K8s · Redis · PostgreSQL ·
高并发 / high concurrency

## Tier 4 — differentiators

MCP Server 开发 / MCP server development · Agent 框架源码研究 / framework
source study · Agent 系统设计 / agent system design · 开源贡献 / open-source
contributions · 技术博客 / technical blog · Prompt Cache 优化 · 语义缓存 /
semantic caching

## Rules

- Density: each target-JD keyword appears 2–3 times, folded into real evidence.
- Never pad: a keyword the candidate cannot defend in an interview is a trap,
  not a boost (rubric dimension 5).
- ASCII keywords match on word boundaries — `github` does not satisfy `git`;
  don't game the lint, satisfy it.

## Per-role tuning

| Target role | Lead project | Front-load in skills |
|---|---|---|
| AI Agent 开发工程师 / AI Agent Engineer | framework / Agent system project | MCP、Agent 框架、asyncio |
| LLM 应用工程师 / LLM Application Engineer | RAG / AI assistant application | RAG、向量数据库、Prompt Engineering |
| 大模型算法工程师 / LLM Algorithm Engineer | model training project | PyTorch、Transformer、SFT/DPO/LoRA |
| AI 产品经理 / AI Product Manager | user-facing application project | product thinking over tech detail |

## JD matching method

1. Extract every hard requirement and keyword from the JD
   (worked inputs: `assets/jd-sample.md` zh, `assets/jd-sample-en.md` en).
2. Map each keyword to concrete resume evidence (bullet + number).
3. Unmappable keywords go into the scorecard as `gaps` — reported honestly,
   never stuffed.
4. Reorder skills/projects so the strongest mapped evidence sits first.
