---
name: design-review
description: Independently challenge a completed requirement design for semantic correctness, domain alignment, omissions, over-design, security and test sufficiency.
---

# Design Review

本 Skill 必须由未参与当前 Design 生成的独立上下文执行。

## 最小输入

1. `python tools/context.py <CHG-ID> --bundle` 输出；
2. 当前 Change 的 `proposal.md`、Spec、`design.yaml`、`design.md`、`tests.yaml`；
3. 必要时再打开 Context Pack 引用的正式原文。

## 评审顺序

1. 检查 Design 是否实现全部 Spec，且没有静默引入 Spec 之外的新业务行为；
2. 检查 FACT 来源是否支持结论，ASM 是否被错误当成事实，OPEN 是否遗漏；
3. 挑战领域模型、规则、不变量、状态和边界，重点检查身份、关系维度、证据审核和数据归属；
4. 检查主流程、异常流程、权限、隐私、失败、一致性、迁移和回滚是否完整；
5. 检查模块依赖是否符合 Decision 与 Context Map，是否出现过度抽象、万能模型或不必要的异步化；
6. 检查测试是否覆盖正例、反例、边界、权限、并发/幂等和隐私，公共 Seam 是否能在实现前稳定约定；
7. 将结论分为 Error、Warning、Review-only，并给出对应的 Spec/Definition/Test ID；
8. 任何阻断项未关闭时，不得批准 Spec Gate。

不得修改设计来让自己的评审通过；评审只输出问题、证据和建议，由设计 Agent 或负责人修订。
