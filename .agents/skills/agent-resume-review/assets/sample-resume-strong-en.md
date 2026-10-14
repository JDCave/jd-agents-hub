# Jordan Lee | AI Agent Engineer

(415) 555-0177 | jordan.lee@example.com | github.com/jordanlee-dev
Seattle, WA

## Education

B.S. Computer Science, State University
GPA 3.6/4.0 | Coursework: Data Structures, Operating Systems, Machine Learning, Deep Learning

## Technical Skills

- Languages: Python (expert), TypeScript (proficient), Go (familiar)
- AI/LLM: Prompt Engineering, RAG system design, agent architecture, MCP protocol, function calling
- Agent frameworks: Nanobot (source-level understanding), LangChain (project work)
- Model training: PyTorch, Transformer architecture, SFT/DPO, LoRA fine-tuning
- Backend & engineering: FastAPI, PostgreSQL, Redis, Milvus (vector database), Docker, asyncio, Git, CI/CD

## Experience

### Enterprise AI Assistant on Nanobot — Feb 2026 to Apr 2026

Stack: Python, Nanobot, MCP, Claude API, FastAPI, Redis, Docker

- Studied the framework core (about 4,000 lines): execution loop, memory management, registry design; published 12 deep-dive engineering notes
- Built 5 custom MCP servers (database query, document retrieval, scheduling, Jira, notifications), standardizing how agents reach internal systems
- Designed 8 progressive-disclosure skills loaded on demand; system-prompt token usage down 40%
- Added a Redis semantic cache: 35% hit rate, 25% lower monthly LLM API spend
- Shipped to production: 500+ conversations/day, 94% successful function calls, 4.2/5 user rating

### MCP Server Cluster — Mar 2026 to Apr 2026

Stack: Python, MCP SDK, JSON-RPC 2.0, FastAPI, Docker, PostgreSQL

- Designed the shared security layer: API-key auth, JSON Schema parameter validation, destructive-operation confirmation, audit logging across all 8 servers
- Implemented stdio and HTTP+SSE dual transports, cutting local end-to-end debug time by 50%
- Iterated server descriptions until LLM calling accuracy rose from 78% to 95%
- Adopted by 3 different agent applications; onboarding time dropped from 2 weeks to 2 days

## Highlights

- Open-sourced 2 general-purpose MCP servers, 200+ GitHub stars combined
- Writes a regular blog series on agent internals
