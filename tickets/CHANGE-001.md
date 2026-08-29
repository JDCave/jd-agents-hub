---
branch: (none)
created: 2026-08-29
id: CHANGE-001
status: open
tag: (none)
title: 新增变更工单管理工作流
type: idea
updated: 2026-08-29
---

## 问题描述 / 需求描述

需要一个针对本 repo 的问题/需求管理机制：用户提出**问题**（使用 agents/skills 过程中遇到的 bug）或**想法**（新需求）时，记录为带编号的 markdown 工单（`tickets/CHANGE-NNN.md`），随后创建 `feature/CHANGE-NNN-xxx` 分支修复或实现，经仓库门禁验证、用户验收后打语义化 tag（首个 v0.1.0；problem=patch、idea=minor），最后用 gh CLI 创建 PR 回 main。整个流程需对齐 doc/harness-engineering.md 的五子系统（工单=State，验收标准=Scope，门禁=Verification，SKILL.md=Instructions，按工单恢复=Session Lifecycle）。

## 验收标准

- [ ] `.agents/skills/change-management/` 结构完整（SKILL.md ≤100 行 + scripts/assets/references/examples/expected_outputs/tests）
- [ ] skill_gate 对 change-management 判 PASS（质量分 ≥90），全仓 audit_skills 无 ERROR
- [ ] ticket_utils.py 三条子命令（new-ticket / next-id / next-version）可用，单元测试全部通过
- [ ] 本工单 CHANGE-001 自身按工作流完成 record → start → verify，状态推进在进展日志留痕

## 验证证据

| 命令 | 退出码 | 结果 |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py .agents/skills/change-management --update-registry | 0 | PASS（quality 91.3/90，8 项检查全过） |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | 6 skills 全部 6/6，无 ERROR |
| python -m unittest discover -s tests（change-management 目录下） | 0 | 11/11 OK |

## 进展日志

- 2026-08-29 — open：工单创建

## 验收记录

（待用户验收：结论 / 日期 / 备注）

## 发布记录

- 版本：(pending，验收后由 next-version 计算，预期 v0.1.0)
- tag：(pending)
- PR：(pending)
- 合并日期：(pending)
