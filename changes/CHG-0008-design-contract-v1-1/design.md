---
contract_version: 1
change: CHG-0008
status: approved
capabilities: []
specs:
  - SPEC-GOV-V11-001
  - SPEC-GOV-V11-002
  - SPEC-GOV-V11-003
  - SPEC-GOV-V11-004
  - SPEC-GOV-V11-005
affected_domains: []
decisions:
  - DEC-0001
applicability:
  workflow: required
  domain_model: not-applicable
  state_machine: not-applicable
  persistence: not-applicable
  external_api: not-applicable
  ui: not-applicable
  events: not-applicable
  migration: required
  performance: not-applicable
  security_privacy: required
  module_consistency: required
  tests_traceability: required
open_questions: 0
---

# Design

## 方案概览

### 事实、假设与开放问题

- FACT-GOV-V11-001：Design Contract v1 已经成为正式门禁。
- FACT-GOV-V11-002：正式追踪仍依赖复杂 Markdown 表格解析。
- FACT-GOV-V11-003：Issue #15 要求引入机器契约、Context Pack 和独立评审。
- ASM-GOV-V11-001：过渡期保留 v1 Markdown 门禁以保障历史兼容。
- 当前无 OPEN 项。

### 约束与禁止事项

- SEC-GOV-V11-001：AI 不得将无来源推断写成 FACT，阻断假设或开放问题不得进入批准态；由 TEST-DESIGN-V11-003 与 TEST-DESIGN-V11-SEC-001 验证。
- 不删除 `design.md` 八章，不新增平行 PRD/HLD/LLD 目录。
- 不使用机器校验替代领域语义和方案取舍评审。

### 核心设计结论

| ID | 设计结论 | 原因 | 关联 Spec |
|---|---|---|---|
| DESIGN-GOV-V11-001 | `design.yaml` 承载确定性事实与追踪，`design.md` 承载解释 | 降低 AI 解析成本与 Markdown 门禁复杂度 | SPEC-GOV-V11-001、SPEC-GOV-V11-005 |
| DESIGN-GOV-V11-002 | facet 增加 review-required 过渡态 | 强迫 AI 主动判断而不是机械接受模板默认值 | SPEC-GOV-V11-003 |
| DESIGN-GOV-V11-003 | 生成和设计评审使用独立上下文 | 降低确认偏差并保留 Review-only 边界 | SPEC-GOV-V11-004 |

### 业务流程与用例

FLOW-GOV-V11-001：创建 Change → 生成 Context Pack → 编写 Proposal/Spec → 登记 FACT/ASM/OPEN → 收敛 facets → 完成 definitions/traceability → 编写八章 Design → 运行确定性校验 → 独立 design-review → Spec Gate。

UC-GOV-V11-001：AI 在进入 review 前必须将所有 review-required 收敛，并关闭阻断假设和开放问题；否则检查失败。

## 领域与数据影响

N/A: domain_model - 本 Change 不修改任何族谱领域概念、规则和不变量。

N/A: persistence - 本 Change 只维护仓库 YAML/Markdown 资产，不新增业务数据库或数据生命周期。

机器契约新增 FACT、ASM、OPEN、definitions 与 traceability；它们是仓库治理数据，不是族谱业务数据。

## 接口与模块边界

### 模块落位与依赖

| ID | 设计对象 | 代码模块 | 职责 | 允许依赖 |
|---|---|---|---|---|
| MODULE-GOV-V11-001 | 机器契约校验 | tools/validate_design_machine.py | 校验引用、facet、事实、假设、定义与追踪 | Python 标准库、PyYAML、Change资产 |
| MODULE-GOV-V11-002 | Change初始化 | tools/new_change.py | 按类型生成 design.yaml 和 legacy frontmatter | 模板、Capability/Domain/Decision清单 |
| MODULE-GOV-V11-003 | Context Pack | tools/context.py | 精确输出相关 Capability、Domain、Decision 和约束 | 正式产品/领域/决策资产 |
| MODULE-GOV-V11-004 | 独立设计评审 | skills/design-review/SKILL.md | 挑战语义、遗漏、过度设计、安全和测试充分性 | Context Pack、Change工件 |

所有新增工具继续位于 `tools/`，Skill保持直接子目录，符合 DEC-0001。

N/A: state_machine - 本 Change 不引入新的业务状态机，只使用既有 Change/Gate 状态。

N/A: external_api - 本 Change 不新增外部网络接口。

N/A: ui - 本 Change 不新增用户界面。

N/A: events - 本 Change 不新增领域事件或消息契约。

## 安全与隐私

| SEC ID | 风险或约束 | 防护措施 | 数据范围/敏感字段 | 审计 | Test |
|---|---|---|---|---|---|
| SEC-GOV-V11-001 | AI 将推断伪装成事实或绕过阻断问题 | FACT必须有来源，ASM/OPEN显式建模，批准态强门禁 | 不处理真实族人数据 | CI、PR、Gate、Evidence | TEST-DESIGN-V11-003、TEST-DESIGN-V11-SEC-001 |

## 测试 Seam

### 公共测试 Seam

公共 Seam 为 `python tools/validate_design_machine.py`、`python tools/context.py CHG-0008 --bundle` 和 `python tools/check.py` 的退出码与结构化输出。合法仓库返回0，反例返回非0并包含稳定错误关键词。

TRACE-GOV-V11-001：所有正式 Spec 必须由 `design.yaml` Definition、Traceability 与 `tests.yaml` 注册覆盖形成双向一致的机器链路。

### 测试清单

| TEST ID | 类型 | 验证内容 | Seam | 关联规则/不变量/契约 |
|---|---|---|---|---|
| TEST-DESIGN-V11-001 | 正向 | 当前仓库机器设计契约通过 | validate_design_machine.py | SPEC-GOV-V11-001、SPEC-GOV-V11-005 |
| TEST-DESIGN-V11-002 | 正向 | 新Change生成design.yaml与类型化facet | new_change.py | SPEC-GOV-V11-001、SPEC-GOV-V11-003 |
| TEST-DESIGN-V11-003 | 反例 | review-required、无来源FACT和阻断ASM被拒绝 | validate_design_machine.py | SPEC-GOV-V11-002、SPEC-GOV-V11-003 |
| TEST-DESIGN-V11-004 | 正向 | Context Pack可机器读取 | context.py --bundle | SPEC-GOV-V11-004 |
| TEST-DESIGN-V11-005 | 回归 | legacy v1与v1.1统一检查通过 | tools/check.py | SPEC-GOV-V11-001、SPEC-GOV-V11-004、SPEC-GOV-V11-005 |
| TEST-DESIGN-V11-SEC-001 | 安全 | FACT/ASM/OPEN和Test注册表门禁 | validate_design_machine.py | SEC-GOV-V11-001 |
| TEST-DESIGN-V11-TRACE-001 | 追踪 | 全部正式Spec的机器Definition与注册测试双向覆盖 | tools/check.py | TRACE-GOV-V11-001 |

### Spec 追踪矩阵

| Spec ID | Flow/Use Case | Rule/Invariant | Command/Contract | Test |
|---|---|---|---|---|
| SPEC-GOV-V11-001 | FLOW-GOV-V11-001 | DESIGN-GOV-V11-001 | Machine Design Contract | TEST-DESIGN-V11-001、TEST-DESIGN-V11-002、TEST-DESIGN-V11-005、TEST-DESIGN-V11-TRACE-001 |
| SPEC-GOV-V11-002 | UC-GOV-V11-001 | SEC-GOV-V11-001 | Fact/Assumption/Open Contract | TEST-DESIGN-V11-003、TEST-DESIGN-V11-SEC-001、TEST-DESIGN-V11-TRACE-001 |
| SPEC-GOV-V11-003 | UC-GOV-V11-001 | DESIGN-GOV-V11-002 | Facet Contract | TEST-DESIGN-V11-002、TEST-DESIGN-V11-003、TEST-DESIGN-V11-TRACE-001 |
| SPEC-GOV-V11-004 | FLOW-GOV-V11-001 | DESIGN-GOV-V11-003 | Context/Review Contract | TEST-DESIGN-V11-004、TEST-DESIGN-V11-005、TEST-DESIGN-V11-TRACE-001 |
| SPEC-GOV-V11-005 | FLOW-GOV-V11-001 | TRACE-GOV-V11-001 | Traceability Contract | TEST-DESIGN-V11-001、TEST-DESIGN-V11-005、TEST-DESIGN-V11-SEC-001、TEST-DESIGN-V11-TRACE-001 |

## 失败、补偿与回滚

### 事务、一致性、并发与幂等

| FAIL ID | 失败点 | 系统状态 | 用户可见结果 | 补偿/重试/幂等 |
|---|---|---|---|---|
| FAIL-GOV-V11-001 | design.yaml校验失败 | 文件不变，检查非零 | 输出具体字段和ID | 修正后重复执行，结果幂等 |
| FAIL-GOV-V11-002 | Context Pack引用未知资产 | 不输出不可信Bundle | 命令明确报错 | 修复Change引用后重试 |
| FAIL-GOV-V11-003 | v1.1误阻断历史Change | CI失败且PR不可合入 | 定位兼容边界 | 回滚机器校验入口，不修改历史工件 |

### 回滚方案

可从 `tools/check.py` 移除机器校验入口并恢复模板、生成器、Context Pack和Skill；CHG-0001至CHG-0007不需要迁移或回写。

## 迁移方案

MIG-GOV-V11-001：CHG-0001至CHG-0007继续使用Design Contract v1；CHG-0008及以后同时声明 `design_contract_version: 1` 和 `design_machine_contract_version: 1`。v1 Markdown校验继续作为兼容层，正式引用与追踪逐步迁移到 `design.yaml`。

## 备选方案与权衡

### 非功能设计

N/A: performance - 仓库Change规模较小，YAML校验和Context Pack应保持秒级，无需单独容量预算。

### 方案权衡

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| 继续增强Markdown解析 | 不新增文件 | 解析复杂、误报风险继续上升 | 不采用 |
| 完全删除design.md | 机器校验简单 | 人工评审与方案解释能力下降 | 不采用 |
| design.yaml机器事实源 + design.md解释 | AI读取快、校验稳定、人工可读 | 短期双轨维护 | 采用 |

### 风险

| 风险 | 影响 | 缓解措施 | Owner |
|---|---|---|---|
| YAML字段过多 | AI和人工写作成本增加 | 生成器预置、首批Change反馈后精简 | repository-owner |
| 双轨不一致 | 设计解释偏离机器事实 | 独立design-review与PR评审 | design-reviewer |
| 自动校验被误当成语义正确 | 错误业务设计进入实现 | 保留Review-only与人工Gate | spec-reviewer |

### 开放问题

无开放问题；首批V0.1需求设计将验证v1.1字段是否需要进一步精简。
