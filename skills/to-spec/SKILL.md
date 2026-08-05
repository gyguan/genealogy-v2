---
name: to-spec
description: Turn an agreed requirement into an OpenSpec Change and a machine-verifiable design contract without repeating resolved clarification.
---

# To Spec

1. 使用 `tools/new_change.py` 创建 Change，不手工复制模板。
2. 读取 `change.yaml`、Proposal、目标 Release、关联 Capability、受影响 Domain 与 Accepted Decision。
3. 完成 `proposal.md`，明确用户、目标、非目标、范围、风险和成功标准。
4. 按受影响领域编写 Spec Delta；每项要求使用稳定 `SPEC-...` ID，并包含可观察的正常、异常和边界场景。
5. 先填写 `design.md` Frontmatter：Change、Capability、Spec、Domain、Decision 必须与正式资产完全一致。
6. 逐项判定 `applicability`。`required` 必须使用模板规定的稳定 ID 给出可测试设计；`not-applicable` 必须写 `N/A: <facet> - <具体原因>`。
7. 按模板顺序设计：约束与流程 → 领域规则与数据 → 命令、状态、契约与模块 → 安全隐私 → 测试追踪 → 失败回滚 → 迁移 → 权衡风险。
8. 每条 `RULE-...`、`INV-...` 必须同时关联 `SPEC-...` 和 `TEST-...`；每个 Spec 必须出现在测试追踪矩阵。
9. 遇到 Capability/版本冲突、领域边界不清、需要修改 Accepted Decision、关键规则无法确定或需要真实敏感数据时，停止设计并显式记录开放问题，不得猜测。
10. 运行 `python tools/validate_design.py` 和 `python tools/check.py`，再执行 `openspec-validation`。
11. `open_questions` 不为 0、存在 TODO/TBD/待确认、校验失败或阻断问题时，不得批准 Spec Gate，也不得开始编码。
