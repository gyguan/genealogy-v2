---
name: openspec-validation
description: Validate an OpenSpec Change for completeness, machine design-contract compliance, consistency, testability, gate readiness and traceability.
---

# OpenSpec Validation

按以下顺序检查并将结果写入 Change Evidence：

1. Change type/Profile、目标与非目标、Capability/Domain/Decision 引用合法；
2. Proposal 已包含用户、当前/目标流程、业务约束、事实来源、依赖、假设、待澄清问题和验收边界；
3. 每个 Spec 具有稳定 ID 和正常、异常、边界验收场景；
4. `design.yaml.references` 与 `change.yaml`、Capability、Spec、Domain、Decision 完全一致；
5. FACT 有可追溯来源，ASM 显式标记状态和阻断性，OPEN 有负责人；AI 推断没有伪装成事实；
6. 每个 facet 已从 `review-required` 收敛；required 有原因与稳定设计 ID，not-applicable 有具体原因；
7. Definitions 的类型、章节、依据、Spec/Test 引用合法；每个 Spec 进入机器追踪矩阵；
8. `design.md` 八章与机器契约一致，业务流程、领域规则、命令状态、数据契约、模块边界、安全隐私、失败回滚和迁移不存在阻断缺口；
9. 模块落位符合 Accepted Architecture Decision，依赖符合 `domains/context-map.yaml`；
10. 设计未混淆身份、姓名、家庭角色、谱系归属及不同关系维度，未创建万能关系模型，未绕过证据审核；
11. 批准 Spec Gate 时不得存在阻断假设、开放问题、TODO/TBD/待确认或模板注释；
12. Task 追踪到已有 Spec，声明正式 Test 与 Evidence，并使用稳定公共 Seam。

运行 `python tools/validate_design.py`、`python tools/validate_design_machine.py` 和 `python tools/check.py`。任何确定性校验失败、关键语义冲突或开放阻断问题都必须阻止 Spec Gate 和实现。
