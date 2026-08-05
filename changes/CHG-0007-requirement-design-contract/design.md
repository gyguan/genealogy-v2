---
contract_version: 1
change: CHG-0007
status: approved
capabilities: []
specs:
  - SPEC-GOV-DESIGN-001
  - SPEC-GOV-DESIGN-002
  - SPEC-GOV-DESIGN-003
  - SPEC-GOV-DESIGN-004
  - SPEC-GOV-DESIGN-005
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

### 约束与禁止事项

- SEC-GOV-DESIGN-001：设计契约不得降低 `SECURITY.md`、全局红线、领域不变量和 Accepted Decision 的优先级；由 TEST-DESIGN-SEC-001 验证。
- 不新增平行的 PRD、HLD、LLD 或设计目录，继续使用 Change 六类工件。
- 不要求不适用的状态机、API、事件、页面或持久化设计，避免 AI 为填充模板制造复杂度。

### 核心设计结论

| ID | 设计结论 | 原因 | 关联 Spec |
|---|---|---|---|
| DESIGN-GOV-001 | Change 声明契约版本，Design Frontmatter 声明范围和适用性 | AI 先读取短结构再按需读取正文 | SPEC-GOV-DESIGN-001、SPEC-GOV-DESIGN-002 |
| DESIGN-GOV-002 | 独立 `validate_design.py` 由 `check.py` 统一调用 | 避免通用仓库校验器职责膨胀 | SPEC-GOV-DESIGN-003、SPEC-GOV-DESIGN-004 |
| DESIGN-GOV-003 | CHG-0007 为强制边界 | CHG-0006 已由诊断治理占用并保留历史兼容 | SPEC-GOV-DESIGN-001 |

### 业务流程与用例

FLOW-GOV-DESIGN-001：生成 Change → 读取最小上下文 → 编写 Spec → 填写 Design Frontmatter → 判定 applicability → 完成八章节 → 运行校验 → OpenSpec 评审 → 批准后拆分和实现。

UC-GOV-DESIGN-001：AI 将 Change 从 draft 提升到 review 前，必须删除模板提示、补齐引用与适用性；失败时不得进入批准和实现。

## 领域与数据影响

N/A: domain_model - 本 Change 不增加或修改族谱领域概念、规则和不变量。

N/A: persistence - 本 Change 不新增业务数据、数据库结构或持久化约束。

设计契约只引用正式领域资产，不复制领域事实；未来业务 Change 仍由 `domains/*.md` 和 `domains/context-map.yaml` 提供权威语义。

## 接口与模块边界

### 模块落位与依赖

| ID | 设计对象 | 代码模块 | 职责 | 允许依赖 |
|---|---|---|---|---|
| MODULE-GOV-DESIGN-001 | 设计契约校验 | tools/validate_design.py | 执行确定性设计校验 | Python标准库、PyYAML、changes资产 |
| MODULE-GOV-DESIGN-002 | 新Change初始化 | tools/new_change.py | 同时初始化 strict Change 与 Design Contract | changes/_template、正式清单 |
| MODULE-GOV-DESIGN-003 | 统一检查 | tools/check.py | 调度诊断、设计、产品和回归检查 | tools下各校验器 |

所有工具保持在 `tools/`，不创建无约束共享目录，符合 DEC-0001。

N/A: state_machine - 本 Change 没有业务实体状态机，只复用既有 Change 状态与 Gate。

N/A: external_api - 本 Change 不新增对外 API 或网络契约。

N/A: ui - 本 Change 只修改仓库治理资产，不提供用户界面。

N/A: events - 本 Change 不发布或订阅领域事件。

## 安全与隐私

| SEC ID | 风险或约束 | 防护措施 | 数据范围/敏感字段 | 审计 | Test |
|---|---|---|---|---|---|
| SEC-GOV-DESIGN-001 | AI 通过自由格式绕过约束 | AGENTS、Skill、Validator、CI和人工Gate四层控制 | 不处理真实族人数据 | PR、Gate、Evidence | TEST-DESIGN-SEC-001 |
| SEC-GOV-DESIGN-002 | 模板诱导提交敏感示例 | 模板禁止真实数据，测试只构造资产反例 | 无真实敏感字段 | CI日志 | TEST-DESIGN-SEC-002 |

## 测试 Seam

### 公共测试 Seam

公共 Seam 为 `python tools/validate_design.py` 和 `python tools/check.py` 的退出码与标准输出。合法仓库返回0，反例返回非0并包含稳定错误关键词。

### 测试清单

| TEST ID | 类型 | 验证内容 | Seam | 关联契约 |
|---|---|---|---|---|
| TEST-DESIGN-001 | 正向 | 当前仓库和 CHG-0007 通过 | validate_design.py | SPEC-GOV-DESIGN-001 |
| TEST-DESIGN-002 | 反例 | 新Change缺契约版本被拒绝 | validate_design.py | SPEC-GOV-DESIGN-001 |
| TEST-DESIGN-003 | 反例 | Design引用不一致被拒绝 | validate_design.py | SPEC-GOV-DESIGN-002 |
| TEST-DESIGN-004 | 反例 | required缺ID或N/A缺原因被拒绝 | validate_design.py | SPEC-GOV-DESIGN-003 |
| TEST-DESIGN-005 | 反例 | Spec或规则测试追踪缺失被拒绝 | validate_design.py | SPEC-GOV-DESIGN-004 |
| TEST-DESIGN-006 | 反例 | 占位、空元数据、伪章节或开放问题被拒绝 | validate_design.py | SPEC-GOV-DESIGN-005 |
| TEST-DESIGN-SEC-001 | 安全 | 根规则与CI继续强制执行 | tools/check.py | SEC-GOV-DESIGN-001 |
| TEST-DESIGN-SEC-002 | 隐私 | 模板和测试不含真实族人数据 | 人工评审 | SEC-GOV-DESIGN-002 |

### Spec 追踪矩阵

| Spec ID | Flow/Use Case | 设计结论 | Contract | Test |
|---|---|---|---|---|
| SPEC-GOV-DESIGN-001 | FLOW-GOV-DESIGN-001 | DESIGN-GOV-003 | Design Contract v1 | TEST-DESIGN-001、TEST-DESIGN-002 |
| SPEC-GOV-DESIGN-002 | FLOW-GOV-DESIGN-001 | DESIGN-GOV-001 | Design Frontmatter | TEST-DESIGN-003 |
| SPEC-GOV-DESIGN-003 | UC-GOV-DESIGN-001 | DESIGN-GOV-001 | Applicability Contract | TEST-DESIGN-004 |
| SPEC-GOV-DESIGN-004 | FLOW-GOV-DESIGN-001 | DESIGN-GOV-002 | Traceability Contract | TEST-DESIGN-005 |
| SPEC-GOV-DESIGN-005 | UC-GOV-DESIGN-001 | DESIGN-GOV-002 | Spec Gate Contract | TEST-DESIGN-006 |

## 失败、补偿与回滚

| FAIL ID | 失败点 | 系统状态 | 用户结果 | 补偿/重试/幂等 |
|---|---|---|---|---|
| FAIL-GOV-DESIGN-001 | Design校验失败 | 文件不变，检查非零 | 输出具体规则 | 修正后重复执行，结果幂等 |
| FAIL-GOV-DESIGN-002 | 生成器无法解析模板 | 不创建误用Change | 命令报错 | 修复后重新创建 |
| FAIL-GOV-DESIGN-003 | CI发现回归 | PR不可合入 | Actions失败 | 修复分支，不绕过门禁 |

回滚可撤销模板、Skill、校验器和生成器变更；若单一facet误报，应通过后续治理Change演进契约，不得删除统一门禁。

## 迁移方案

MIG-GOV-DESIGN-001：CHG-0001 至 CHG-0006 继续使用既有格式；从 CHG-0007 起按 Change ID 和 `design_contract_version: 1` 强制新契约。生成器自动初始化，未来 Change 无需人工迁移。

## 备选方案与权衡

### 非功能设计

N/A: performance - 校验对象为小规模Markdown/YAML资产，当前无需独立性能预算；统一检查保持秒级目标。

### 方案权衡

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| 只扩展自然语言模板 | 改动小 | 无法阻止遗漏和绕过 | 不采用 |
| 二十多个固定章节 | 覆盖全面 | Token高且空洞内容多 | 不采用 |
| Frontmatter+八章节+适用性+Validator | 结构稳定、按需、可校验 | 需维护契约 | 采用 |
| 全部写入validate_repo.py | 单文件 | 职责膨胀 | 不采用 |

### 风险

| 风险 | 影响 | 缓解措施 | Owner |
|---|---|---|---|
| 稳定ID增加书写成本 | 输出变长 | 只对required使用，N/A可跳过 | repository-owner |
| 结构通过但语义错误 | 错误进入实现 | 保留语义校验与人工双轴评审 | repository-owner |
| 前缀规则演进 | 兼容风险 | 通过contract_version演进 | repository-owner |

### 开放问题

无阻断性开放问题。
