---
branch: feature/CHANGE-002-fix-audit-runner
created: 2026-08-29
id: CHANGE-002
status: awaiting-acceptance
tag: (none)
title: audit 脚本在本仓库路径错误无法运行
type: problem
updated: 2026-08-29
---

## 问题描述 / 需求描述

运行仓库级 audit 时脚本报 FileNotFound：RUNNER 指向了源仓库的路径而非本仓库
`.agents/skills/...` 下的实际位置。期望：audit 在本仓库直接可用。

## 验收标准

- [x] audit_skills.py 全仓运行不报 FileNotFound
- [x] 退出码为 0，聚合报告输出正常

## 验证证据

| 命令 | 退出码 | 结果 |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 5 skills audited, no ERROR |

## 进展日志

- 2026-08-29 — open：工单创建
- 2026-08-29 — open → in-progress；分支 feature/CHANGE-002-fix-audit-runner 已创建
- 2026-08-29 — in-progress → awaiting-acceptance；门禁通过，证据见上

## 验收记录

（待用户验收：结论 / 日期 / 备注）

## 发布记录

- 版本：(pending，验收后由 next-version 计算)
- tag：(pending)
- PR：(pending)
- 合并日期：(pending)
