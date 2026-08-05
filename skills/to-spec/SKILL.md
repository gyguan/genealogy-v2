---
name: to-spec
description: Turn an agreed requirement into an OpenSpec Change, a machine design contract and a human-readable design without repeating resolved clarification.
---

# To Spec

1. 使用 `tools/new_change.py` 创建 Change，不手工复制模板。
2. 读取 `change.yaml`、Proposal，并运行 `python tools/context.py <CHG-ID> --bundle` 获取最小上下文。
3. 完成 `proposal.md`：明确用户与角色、当前/目标流程、目标、非目标、范围、业务约束、事实来源、依赖、假设、待澄清问题、风险和验收边界。
4. 按受影响领域编写 Spec Delta；每项要求使用稳定 `SPEC-...` ID，并包含可观察的正常、异常和边界场景。
5. 先填写 `design.yaml.references`，必须与 Change、Capability、Spec、Domain、Decision 完全一致。
6. 将输入分为：已确认事实 `FACT-...`、显式假设 `ASM-...`、开放问题 `OPEN-...`。没有来源的内容不得写成事实。
7. 逐项处理 `facets`。生成器给出的 `review-required` 只是待判断状态；进入 review 前必须改为 `required` 或 `not-applicable`。
8. 在 `design.yaml.definitions` 中定义稳定设计 ID、类型、章节、摘要、依据、Spec 和 Test；在 `traceability` 中完成每个 Spec 的设计/Test 覆盖。
9. 再按 `design.yaml` 编写 `design.md` 八章解释：约束与流程 → 领域规则与数据 → 命令、状态、契约与模块 → 安全隐私 → 测试 → 失败回滚 → 迁移 → 权衡风险。
10. 遇到 Capability/版本冲突、领域边界不清、需要修改 Accepted Decision、关键规则无法确定或需要真实敏感数据时，停止设计并记录阻断假设或开放问题，不得猜测。
11. 运行 `python tools/validate_design.py`、`python tools/validate_design_machine.py` 和 `python tools/check.py`，再执行 `openspec-validation`。
12. 阻断假设未确认、存在开放问题、存在 `review-required`、校验失败或语义评审阻断时，不得批准 Spec Gate，也不得开始编码。
