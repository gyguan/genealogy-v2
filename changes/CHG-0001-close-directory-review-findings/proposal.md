# Proposal

## 背景与问题

目录评审确认当前轻量结构方向正确，但仍存在指令优先级冲突、Change 状态与 Gate 不可校验、领域依赖重复维护、追踪链不完整、Capability 与 Glossary 为空、Decision 生命周期不足、代码落位未决和校验器过度禁止未来目录等问题。

## 关联产品能力

本 Change 属于仓库治理类型，不直接实现单一产品能力，但为全部 P0 能力提供一致的研发与验证基线。

## 目标

- 消除规则和领域依赖的多事实源；
- 让 Change、Gate、Spec、Task 和 Evidence 可以自动校验；
- 建立最小 Capability、Glossary 和领域依赖基线；
- 固化首期代码布局 Decision；
- 保持当前顶层目录轻量且允许经 Decision 演进。

## 非目标

- 不创建空业务代码目录；
- 不实现族谱业务功能；
- 不引入重型工作流、Schema 平台或知识索引系统。

## 用户场景

AI 接到需求后能够确定权威资产、合法修改边界、领域依赖和当前有效 Decision，并在合入前证明 Spec、Task 与 Evidence 闭环。

## 范围与影响领域

影响全仓治理以及六个领域的基础描述和依赖图，不改变具体业务实现。

## 关联 Decision

- `DEC-0001`：领域对齐的模块化单体代码布局。

## 必读上下文

- `AGENTS.md`
- `product/capability-map.yaml`
- `domains/glossary.yaml`
- `domains/context-map.yaml`
- 上次目录结构评审结论

## 允许修改

产品、领域、Change 模板、Decision 模板、校验工具、README 和 GitHub 门禁。

## 禁止修改

不创建业务实现，不复制旧仓代码，不降低安全与审核红线。

## 风险

校验规则过严可能阻塞合理演进，因此仅永久禁止已废弃路径；新增顶层资产通过 Change 和 Decision 批准。

## 成功标准

- 本仓正向样本通过 `python tools/validate_repo.py`；
- 非法 Gate、未知依赖、循环依赖、重复 ID、缺失 Spec/Evidence 等反例被阻断；
- 所有评审 P0 问题均有对应资产或自动校验规则。
