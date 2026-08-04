# 贡献规则

## 基本流程

```text
创建 Change
→ Proposal / Specs / Design
→ 自动校验与人工评审
→ 纵向 Ticket 与开发任务包
→ TDD 实现
→ 双轴评审
→ 仓库门禁
→ 合入基线
→ 归档 Change
```

## 提交要求

- 非平凡 PR 必须关联 Change ID。
- PR 描述必须列出 Spec、Ticket、验证命令和证据位置。
- 正式领域语义进入 `domains/`，单次增量进入 `changes/active/`。
- 长期且难逆的权衡进入 `decisions/`。
- 非权威研究进入 `reference/`。
- 禁止 `final-v2`、`latest`、`new` 等相对文件名。
