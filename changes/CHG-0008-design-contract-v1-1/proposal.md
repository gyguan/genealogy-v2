# Proposal

## 背景与问题

Design Contract v1 已能阻断结构、引用和追踪缺口，但确定性关系仍主要从 Markdown 表格推导，Proposal 对用户、流程、事实来源、假设和验收边界表达不足，生成与语义评审也未完全分离。这会增加 AI 读取成本，并让“格式正确但语义错误”的设计进入评审。

## 目标用户与角色

直接用户是执行需求设计、评审和实现的 AI Agent、产品/领域负责人、架构师与代码 Reviewer；仓库维护者负责治理规则和门禁演进。

## 当前流程与痛点

当前流程为 Proposal → Spec → Design Markdown → 自动校验 → 人工评审。AI需要从多份原文自行拼装事实，并依赖复杂 Markdown 结构表达正式追踪关系；同一 Agent 常连续生成和自检，确认偏差较强。

## 目标业务流程

创建 Change 后生成最小 Context Pack，AI先登记 FACT/ASM/OPEN，再完成机器契约和八章设计解释；确定性校验通过后，由独立 Design Review 挑战业务语义，最后才允许批准 Spec Gate。

## 关联产品能力

本 Change 属于仓库治理，不新增或修改产品 Capability；它服务后续全部产品、领域和工程 Change。

## 目标

新增 `design.yaml` 机器事实源，增强 Proposal 输入，按 Change 类型初始化 facet，引入 `review-required`，提供 `context.py --bundle`，新增独立 `design-review` Skill，并保持 Design Contract v1 历史兼容。

## 非目标

不删除 `design.md` 八章，不把业务语义交给 Python 自动裁决，不重写完整 Markdown 解析器，不修改族谱产品能力、领域事实或业务代码。

## 范围与影响领域

更新 Change 模板、生成器、上下文工具、AI规则、设计相关 Skill、统一检查、机器契约校验器和回归测试；不影响任何族谱领域上下文。

## 核心业务约束

机器契约与正式 Change/Spec/Test 必须双向一致；FACT 必须有来源；阻断假设和开放问题在评审前关闭；生成与独立评审不得由同一上下文冒充完成。

## 需求事实来源

- 产品能力：本 Change 无 Capability。
- 领域不变量：本 Change 不修改领域不变量。
- Accepted Decision：DEC-0001 约束工具与模块落位。
- Issue / 用户确认：Issue #15 与本次用户指令。

## 依赖与前置条件

依赖已合入的 CHG-0007 Design Contract v1、strict Change、`tests.yaml` 注册表、`tools/check.py` 和最小上下文工具。

## 假设

保留 v1 Markdown 门禁作为兼容层，v1.1 先把正式引用和追踪迁移到 YAML，后续再根据真实使用数据决定是否简化 Markdown 解析器。

## 待澄清问题

无阻断问题；机器契约字段将在首批真实业务 Change 中继续验证易用性。

## 关联 Decision

遵守 DEC-0001；新增工具继续放在 `tools/`，Skill保持单一职责，不创建平行 PRD/HLD/LLD 目录。

## 风险

双轨契约会短期增加少量维护成本；YAML过细可能增加写作负担；自动校验仍不能证明领域语义正确。通过生成器初始化、Context Pack、独立评审和历史兼容降低风险。

## 成功标准

CHG-0008 起自动生成 `design.yaml`；机器契约与 Change/Spec/Test 一致；review-required 在评审前收敛；Context Pack可用；独立Design Review被纳入流程；`python tools/check.py`通过。

## 验收边界

验收覆盖仓库治理资产、生成器、校验器、Context Pack和Skill；不以本 Change 验收任何族谱业务功能或真实用户数据。
