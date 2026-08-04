---
name: openspec-validation
description: Validate an OpenSpec Change for completeness, design-contract compliance, consistency, testability, gate readiness and traceability.
---

# OpenSpec Validation

按以下顺序检查并将结果写入 Change Evidence：

1. Change type/Profile、目标与非目标、Capability/Domain/Decision 引用合法；
2. 每个 Spec 具有稳定 ID 和正常、异常、边界验收场景；
3. Design Frontmatter 与 `change.yaml`、Spec 文件完全一致，`applicability` 已逐项判定；
4. `required` 设计项具有规定的稳定 ID，`not-applicable` 项具有具体 N/A 原因；
5. 业务流程、领域规则、命令状态、数据契约、模块边界、安全隐私、失败回滚和迁移内容不存在阻断缺口；
6. 每条 Rule/Invariant 同时关联 Spec 与 Test，每个 Spec 进入测试追踪矩阵；
7. 模块落位符合 Accepted Architecture Decision，依赖符合 `domains/context-map.yaml`；
8. 设计未混淆身份、姓名、家庭角色、谱系归属及不同关系维度，未创建万能关系模型，未绕过证据审核；
9. `open_questions` 与实际 OPEN 项一致；批准 Spec Gate 时必须为 0，且不得残留 TODO、TBD、待确认或模板注释；
10. Task 追踪到已有 Spec，声明测试与 Evidence，并使用稳定公共 Seam。

运行 `python tools/validate_design.py` 和 `python tools/check.py`。任何确定性校验失败、关键语义冲突或开放阻断问题都必须阻止 Spec Gate 和实现。
