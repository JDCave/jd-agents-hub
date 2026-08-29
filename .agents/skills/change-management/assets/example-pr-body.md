## Summary

[CHANGE-NNN] <标题>

## What & why

（从工单「问题描述 / 需求描述」复制或改写：做了什么、为什么）

## Acceptance criteria

- [x] （从工单复制验收标准，逐条勾选）

## Verification evidence

| 命令 | 退出码 | 结果 |
| --- | --- | --- |
| python .agents/skills/skill-tester/scripts/skill_gate.py --all | 0 | all PASS |
| python .agents/skills/skill-tester/scripts/audit_skills.py | 0 | no ERROR |

## Release

- tag: vX.Y.Z（本 PR 对应的验收 tag）
- ticket: tickets/CHANGE-NNN.md
