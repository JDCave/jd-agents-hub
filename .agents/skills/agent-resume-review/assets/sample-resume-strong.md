# 李四 | AI Agent 开发工程师

📞 139-0000-0000 | 📧 lisi@example.com | 🔗 github.com/lisi-dev
📍 上海 | 期望薪资:面议

## 教育背景

XX大学 计算机科学与技术 本科 2022.09 - 2026.06
GPA 3.6/4.0 | 核心课程:数据结构、操作系统、机器学习、深度学习

## 技术技能

- 编程语言:Python(精通)、TypeScript(熟悉)、Go(了解)
- AI/LLM:Prompt Engineering、RAG 系统设计、Agent 架构、MCP 协议、Function Calling
- Agent 框架:Nanobot(源码级理解)、LangChain(项目实践)
- 模型训练:PyTorch、Transformer 架构、SFT/DPO、LoRA 微调
- 后端与工程:FastAPI、PostgreSQL、Redis、Milvus(向量数据库)、Docker、asyncio 异步编程、Git、CI/CD

## 项目经历

### 基于 Nanobot 的企业智能助手系统  2026.02 - 2026.04

技术栈:Python、Nanobot、MCP、Claude API、FastAPI、Redis、Docker

- 系统研读 Nanobot 核心源码(约 4000 行),深入理解 AgentLoop 的 ReAct 执行流程与记忆管理设计,输出 12 篇深度技术文档
- 基于 MCP 协议开发 5 个自定义工具服务器(数据库查询、文档检索、日程管理、Jira 集成、飞书通知),实现企业内部系统与 Agent 的标准化连接
- 设计 8 个领域 Skill 并利用渐进披露机制按需加载,system prompt token 占用减少 40%
- 实现 Redis 语义缓存层,相似查询命中率 35%,LLM API 月度成本降低 25%
- 系统上线后日均处理 500+ 次对话请求,工具调用成功率 94%,用户满意度 4.2/5

### 企业级 MCP 工具服务器集群开发  2026.03 - 2026.04

技术栈:Python、MCP SDK、JSON-RPC 2.0、FastAPI、Docker、PostgreSQL

- 设计统一安全框架:API Key 认证、JSON Schema 参数校验、敏感操作确认注解、审计日志,覆盖全部 8 个服务器
- 实现 stdio 与 HTTP+SSE 双传输模式,本地调试效率提升,生产环境支持多用户共享
- 迭代优化工具描述文档,LLM 工具调用准确率从 78% 提升至 95%
- 集群接入 3 个不同 Agent 应用,新应用接入周期从 2 周缩短到 2 天

## 个人亮点

- GitHub 开源 2 个通用 MCP Server,累计 200+ stars
- 持续输出 AI Agent 方向技术博客,善于从源码理解设计思想
