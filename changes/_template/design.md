---
contract_version: 1
change: CHG-0000
status: draft
capabilities: []
specs: []
affected_domains: []
decisions: []
applicability:
  workflow: required
  domain_model: required
  state_machine: not-applicable
  persistence: not-applicable
  external_api: not-applicable
  ui: not-applicable
  events: not-applicable
  migration: not-applicable
  performance: not-applicable
  security_privacy: required
  module_consistency: required
  tests_traceability: required
open_questions: 0
---

# Design

> `design.yaml` 是范围、事实、假设、适用性、稳定 ID 和 Spec/Test 追踪的机器事实源；本文只解释方案及取舍。先完成机器契约，再按其中的定义 ID 编写八个固定章节。进入评审前删除所有注释、TODO、TBD 和待确认占位。

## 方案概览

### 事实、假设与开放问题

<!-- 只引用 design.yaml 中的 FACT-...、ASM-...、OPEN-...，不要在正文静默新增事实或假设。 -->

### 约束与禁止事项

<!-- 引用正式领域不变量、Accepted Decision、安全红线和兼容约束。安全/隐私约束使用 SEC-... ID。 -->

### 核心设计结论

| ID | 设计结论 | 原因 | 关联 Spec |
|---|---|---|---|

### 业务流程与用例

<!-- 流程使用 FLOW-...，用例使用 UC-...；至少说明参与者、前置条件、主流程、异常流程和后置状态。 -->

## 领域与数据影响

### 模型、规则与不变量

| ID | 类型 | 设计内容 | 执行位置 | 关联 Spec | 验证测试 |
|---|---|---|---|---|---|

<!-- MODEL-...、RULE-...、INV-... 必须与 design.yaml definitions 一致。 -->

### 数据结构与完整性

| ID | 对象/约束 | 类型或结构 | 完整性保护 | 敏感级别 | 验证测试 |
|---|---|---|---|---|---|

<!-- 持久化适用时使用 DATA-... 或 CONSTRAINT-...；否则解释机器契约中的不适用结论。 -->

## 接口与模块边界

### 模块落位与依赖

| ID | 设计对象 | 代码模块 | 职责 | 允许依赖 |
|---|---|---|---|---|

<!-- 使用 MODULE-...，必须遵守 Accepted 架构 Decision 和 domains/context-map.yaml。 -->

### 命令、状态与权限

| Command ID | 输入 | 前置条件/Guard | 状态结果 | 权限 | 失败码 | Spec | Test |
|---|---|---|---|---|---|---|---|

<!-- 状态机适用时使用 CMD-...、STATE-...、PERM-...、ERR-...。 -->

### API、事件与页面契约

| ID | 类型 | 输入/触发 | 输出/结果 | 错误/版本策略 | Spec | Test |
|---|---|---|---|---|---|---|

<!-- 分别使用 API-...、EVENT-...、UI-...；不适用时解释机器契约中的原因。 -->

## 安全与隐私

| SEC ID | 风险或约束 | 防护措施 | 数据范围/敏感字段 | 审计 | Test |
|---|---|---|---|---|---|

<!-- 安全与隐私默认为 required；至少包含一个与 design.yaml 一致的 SEC-...。 -->

## 测试 Seam

### 公共测试 Seam

<!-- 说明可在实现前约定、实现后稳定调用的公共测试边界。 -->

### 测试清单

| TEST ID | 类型 | 验证内容 | Seam | 关联规则/不变量/契约 |
|---|---|---|---|---|

### Spec 追踪矩阵

| Spec ID | Flow/Use Case | Rule/Invariant | Command/Contract | Test |
|---|---|---|---|---|

<!-- 本表用于人工阅读；正式追踪关系以 design.yaml traceability 与 tests.yaml 为准。 -->

## 失败、补偿与回滚

### 事务、一致性、并发与幂等

| FAIL ID | 失败点 | 系统状态 | 用户可见结果 | 补偿/重试/幂等 |
|---|---|---|---|---|

### 回滚方案

<!-- 说明代码、配置和数据的回滚边界；不可回滚部分必须明确。 -->

## 迁移方案

<!-- 适用时使用 MIG-... 描述迁移、兼容、校验和回退。 -->

## 备选方案与权衡

### 非功能设计

<!-- 性能适用时使用 NFR-...。 -->

### 方案权衡

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|

### 风险

| 风险 | 影响 | 缓解措施 | Owner |
|---|---|---|---|

### 开放问题

<!-- 只展开 design.yaml 中的 OPEN-...；批准 Spec Gate 前必须为空。 -->
