---
contract_version: 1
change: CHG-0008
status: approved
capabilities: []
specs:
  - SPEC-GOV-BOUNDARY-001
  - SPEC-GOV-BOUNDARY-002
  - SPEC-GOV-BOUNDARY-003
affected_domains: []
decisions: []
applicability:
  workflow: required
  domain_model: not-applicable
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

## 方案概览

### 约束与禁止事项

- SEC-GOV-BOUNDARY-001：修复只能强化确定性最低正确性，不得把 Decision 语义质量、架构优劣或风险接受编码为自动裁决；由 TEST-GOV-BOUNDARY-SEC-001 验证。
- 保持现有 `validate_*_strict.py` 入口和 Error/Warning/Review-only 边界，不通过放宽所有文件类型消除误报。
- GitHub Base 内容只用于重命名和删除文件的历史元数据校验，不写入仓库或日志。

### 核心设计结论

| ID | 设计结论 | 原因 | 关联 Spec |
|---|---|---|---|
| DESIGN-GOV-BOUNDARY-001 | PR 核心校验保留 GitHub changed-file 元数据并将 Base SHA 传给 strict 入口 | 旧路径类型只能从变更前版本确定 | SPEC-GOV-BOUNDARY-001 |
| DESIGN-GOV-BOUNDARY-002 | Decision 类型映射只接受 canonical schema，并将 architecture/compliance 映射到现有 Change 类型 | 避免两个校验器标准分叉 | SPEC-GOV-BOUNDARY-001 |
| DESIGN-GOV-BOUNDARY-003 | Spec 在结构扫描前屏蔽 fenced block | 示例标题不是正式需求资产 | SPEC-GOV-BOUNDARY-002 |
| DESIGN-GOV-BOUNDARY-004 | Design 分离“可中断开放段落”与“该行结束后仍有开放段落” | 列表块边界不能等价于列表项正文状态 | SPEC-GOV-BOUNDARY-003 |

### 业务流程与用例

FLOW-GOV-BOUNDARY-001：读取 PR changed files → 判断 Head/Base 内容来源 → 解析正式 Decision 元数据或治理文档 → 校验声明 Change 类型 → 输出确定性诊断。

UC-GOV-BOUNDARY-001：Contributor 在 Spec 或 Design 中加入 Markdown 示例时，校验器只读取渲染后的正式结构，示例和引用不能提供正式 ID，合法列表正文也不能被误删。

## 领域与数据影响

N/A: domain_model - 本 Change 不增加或修改族谱领域模型、业务规则和领域不变量。

N/A: persistence - 本 Change 不新增数据库、文件格式或持久化业务数据；仅在 CI 内存中读取 GitHub 元数据。

## 接口与模块边界

### 模块落位与依赖

| ID | 设计对象 | 代码模块 | 职责 | 允许依赖 |
|---|---|---|---|---|
| MODULE-GOV-BOUNDARY-001 | PR 文件上下文 | tools/validate_pr_change.py | 保留 changed-file 状态并传递 repo/token/base SHA | Python 标准库、GitHub REST |
| MODULE-GOV-BOUNDARY-002 | Decision 范围解析 | tools/validate_pr_change_strict.py | 解析 canonical 类型与 Head/Base 内容 | validate_pr_change、PyYAML |
| MODULE-GOV-BOUNDARY-003 | Spec 可见结构 | tools/validate_change_quality_strict.py | 屏蔽 fenced block 后解析 Spec/Scenario | validate_change_quality |
| MODULE-GOV-BOUNDARY-004 | Design 段落状态 | tools/validate_design.py | 修正 lazy quote 与列表项开放段落状态 | 现有 Design 校验核心 |

N/A: state_machine - 本 Change 不新增业务状态机，只调整 Markdown 解析状态的内部实现。

N/A: external_api - 不新增对外 API；仅复用 GitHub Contents API 读取 PR Base 文件。

N/A: ui - 本 Change 不提供用户界面。

N/A: events - 本 Change 不发布或订阅领域事件。

## 安全与隐私

| SEC ID | 风险或约束 | 防护措施 | 数据范围/敏感字段 | 审计 | Test |
|---|---|---|---|---|---|
| SEC-GOV-BOUNDARY-001 | Base 文件内容可能被错误输出或扩大读取范围 | 只按 changed-file 精确路径读取，解析后不打印正文，仅输出路径和诊断码 | 公开仓库治理文件，无族人数据 | GitHub Actions 与 PR Review | TEST-GOV-BOUNDARY-SEC-001 |

## 测试 Seam

### 公共测试 Seam

公共 Seam 为 `validate_declared_scope()`、`required_change_types()`、`validate_change_quality_strict.py` 和 `validate_design.py` 的返回诊断、退出码与稳定错误文本。Base 内容在单元测试中通过 `base_content` 注入，在线 CI 使用 GitHub Contents API。

### 测试清单

| TEST ID | 类型 | 验证内容 | Seam | 关联规则/不变量/契约 |
|---|---|---|---|---|
| TEST-GOV-BOUNDARY-001 | 正反例 | canonical Decision、README、rename/delete Base 内容 | validate_pr_change_strict | SPEC-GOV-BOUNDARY-001 |
| TEST-GOV-BOUNDARY-002 | 正向 | fenced Spec 示例不产生正式结构 | validate_change_quality_strict | SPEC-GOV-BOUNDARY-002 |
| TEST-GOV-BOUNDARY-003 | 正反例 | lazy quote 与列表项正文段落状态 | validate_design | SPEC-GOV-BOUNDARY-003 |
| TEST-GOV-BOUNDARY-SEC-001 | 集成 | 当前仓库全部治理与回归检查 | tools/check.py | SEC-GOV-BOUNDARY-001 |

### Spec 追踪矩阵

| Spec ID | Flow/Use Case | Rule/Invariant | Command/Contract | Test |
|---|---|---|---|---|
| SPEC-GOV-BOUNDARY-001 | FLOW-GOV-BOUNDARY-001 | DESIGN-GOV-BOUNDARY-001、DESIGN-GOV-BOUNDARY-002 | PR Decision Scope Contract | TEST-GOV-BOUNDARY-001、TEST-GOV-BOUNDARY-SEC-001 |
| SPEC-GOV-BOUNDARY-002 | UC-GOV-BOUNDARY-001 | DESIGN-GOV-BOUNDARY-003 | Spec Visible Markdown Contract | TEST-GOV-BOUNDARY-002、TEST-GOV-BOUNDARY-SEC-001 |
| SPEC-GOV-BOUNDARY-003 | UC-GOV-BOUNDARY-001 | DESIGN-GOV-BOUNDARY-004 | Design Paragraph Contract | TEST-GOV-BOUNDARY-003、TEST-GOV-BOUNDARY-SEC-001 |

## 失败、补偿与回滚

### 事务、一致性、并发与幂等

| FAIL ID | 失败点 | 系统状态 | 用户可见结果 | 补偿/重试/幂等 |
|---|---|---|---|---|
| FAIL-GOV-BOUNDARY-001 | GitHub Base 内容读取失败 | PR 检查失败，不产生错误放行 | 输出 PR-DECISION-001 与路径 | Token/网络恢复后重跑，读取幂等 |
| FAIL-GOV-BOUNDARY-002 | Markdown 边界回归 | Repository Validation 失败 | 输出对应测试失败 | 修复解析函数并重跑全部回归 |
| FAIL-GOV-BOUNDARY-003 | strict 入口与 core 签名不一致 | PR 在线检查失败 | 输出 PR-EXEC-001 | 保留兼容参数并由单元测试覆盖 |

### 回滚方案

可分别回滚四个校验器文件与新增测试；回滚后必须恢复对相关 Markdown 写法和 Decision rename/delete 的临时限制，不得通过跳过 `pr-governance` 放行。

## 迁移方案

N/A: migration - 本 Change 不改变仓库资产 schema 或历史数据；代码上线后立即适用于后续 PR，无需迁移现有 Change。

## 备选方案与权衡

### 非功能设计

N/A: performance - 每个 PR 仅对 changed Decision 文件增加一次 Base Contents 读取，文件数量和体积有限，无需独立性能预算。

### 方案权衡

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| 缺失旧文件时允许全部 Change 类型 | 实现简单 | 删除 Decision 可绕过类型门禁 | 不采用 |
| 引入完整 CommonMark AST 库 | 语义更完整 | 增加依赖和复杂度，超出本 Change 范围 | 暂不采用 |
| 在现有轻量状态机中修复已确认边界 | 改动可控、回归明确 | 仍需持续评审边缘语法 | 采用 |

### 风险

| 风险 | 影响 | 缓解措施 | Owner |
|---|---|---|---|
| GitHub API 返回格式变化 | 历史 Decision 无法解析 | 严格校验 payload 并输出确定性错误 | repository-owner |
| Markdown 新边界再次出现 | 合法文档误报或示例漏检 | 正反例配对、最终 Head Codex Review | repository-owner |

### 开放问题

无开放问题。
