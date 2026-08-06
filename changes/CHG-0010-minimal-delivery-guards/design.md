---
contract_version: 1
change: CHG-0010
status: approved
capabilities: []
specs:
  - SPEC-GOV-MIN-001
  - SPEC-GOV-MIN-002
  - SPEC-GOV-MIN-003
  - SPEC-GOV-MIN-004
  - SPEC-GOV-MIN-005
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

- FACT-GOV-MIN-001：当前 `tools/check.py` 只验证 Test Registry 结构，没有执行 PR 声明 Change 的注册命令。
- FACT-GOV-MIN-002：当前 PR 范围校验以目录和 Change 类型为主，尚未精确到 Domain、Decision、Capability ID。
- FACT-GOV-MIN-003：仓库规则已经要求 high-risk Change 获得独立人类 APPROVED。
- ASM-GOV-MIN-001：Python、Node、Maven、Gradle Runner 可以覆盖近期项目测试需求。
- 当前无 OPEN 项。

### 约束与禁止事项

- SEC-GOV-MIN-001：PR 控制的注册测试必须使用白名单 Runner、单命令超时和最小环境，不得继承 GitHub Token；high-risk 只接受非作者、非 Bot、非 AI Actor 的当前 Head APPROVED。
- 不新增完整状态历史、Issue Contract、Warning 豁免系统或 Changed File 到 Task 的全链路映射。
- 普通 standard/lightweight Change 不增加额外人类审批。

### 核心设计结论

| ID | 设计结论 | 原因 | 关联 Spec |
|---|---|---|---|
| DESIGN-GOV-MIN-001 | 只执行 PR Body 声明 Change 的 Test Registry | 控制 CI 时间并避免历史 Change 重放 | SPEC-GOV-MIN-001 |
| DESIGN-GOV-MIN-002 | affected 范围只精确到正式 Domain、Decision、Capability | 获得高收益同时避免 Task Scope 维护负担 | SPEC-GOV-MIN-002 |
| DESIGN-GOV-MIN-003 | 占位 ID 只在 Review-ready 后阻断 | 保留生成器效率并保护正式追踪资产 | SPEC-GOV-MIN-003 |
| DESIGN-GOV-MIN-004 | 人类 APPROVED 仅针对 high-risk | 风险分级而不拖慢普通交付 | SPEC-GOV-MIN-004 |

### 业务流程与用例

FLOW-GOV-MIN-001：Contributor 提交 PR → 运行仓库结构与设计校验 → 精确验证 affected 资产 → 在隔离环境执行当前 Change 注册测试 → Codex Review 当前 Head → high-risk 追加人类 APPROVED → Release Approval 绑定最终 Head 和校验结果 → 同一个 PR 更新 completed 并合入。

## 领域与数据影响

N/A: domain_model - 本 Change 不修改任何族谱领域概念、规则或不变量。

N/A: persistence - 本 Change 不新增业务数据库、数据结构或持久化生命周期。

## 接口与模块边界

### 模块落位与依赖

| ID | 设计对象 | 代码模块 | 职责 | 允许依赖 |
|---|---|---|---|---|
| MODULE-GOV-MIN-001 | 注册测试执行器 | tools/run_change_tests.py | 解析当前 PR Change 并安全执行注册命令 | Python 标准库、PyYAML、validate_pr_change |
| MODULE-GOV-MIN-002 | 精确资产范围 | tools/validate_pr_change_strict.py | 比较 Domain、Decision 和 Capability Base/Head 差异 | GitHub Contents API、PyYAML |
| MODULE-GOV-MIN-003 | 占位 ID 门禁 | tools/validate_change_quality_strict.py、tools/validate_design_machine.py | Review-ready 后阻断模板 ID | 现有 Change 与 Design 校验核心 |
| MODULE-GOV-MIN-004 | Profile 感知评审 | tools/validate_pr.py | high-risk 增加当前 Head 人类批准 | GitHub Pull Request API、governance.yaml |

N/A: state_machine - 继续使用既有 Change、Gate 与 PR Review 状态，不新增生命周期。

N/A: external_api - 不新增对外业务 API，只复用已有 GitHub API。

N/A: ui - 本 Change 不新增用户界面。

N/A: events - 本 Change 不新增领域事件或异步消息契约。

## 安全与隐私

| SEC ID | 风险或约束 | 防护措施 | 数据范围/敏感字段 | 审计 | Test |
|---|---|---|---|---|---|
| SEC-GOV-MIN-001 | PR 注册命令读取 Actions 凭证或 high-risk 被 AI 单独放行 | 子进程最小环境、Runner 白名单、超时、非作者人类 APPROVED | GitHub Token 与 PR Review 身份 | Actions 日志、Review、Status | TEST-GOV-MIN-SEC-001 |

## 测试 Seam

### 公共测试 Seam

公共 Seam 包括 `validated_argv()`、`safe_environment()`、`validate_exact_asset_scope()`、`placeholder_identifier()`、`has_current_head_human_approval()` 的返回值与稳定诊断码，以及 Repository Validation 的注册测试阶段退出码。

### 测试清单

| TEST ID | 类型 | 验证内容 | Seam | 关联规则/不变量/契约 |
|---|---|---|---|---|
| TEST-GOV-MIN-001 | 正反例 | 注册命令白名单、shell 拒绝、环境隔离 | run_change_tests | SPEC-GOV-MIN-001 |
| TEST-GOV-MIN-002 | 正反例 | Domain、Decision、Capability 精确声明 | validate_pr_change_strict | SPEC-GOV-MIN-002 |
| TEST-GOV-MIN-003 | 正反例 | 模板稳定 ID 识别 | strict Change、machine Design | SPEC-GOV-MIN-003 |
| TEST-GOV-MIN-004 | 正反例 | Bot、作者、人类批准与后续请求修改 | validate_pr | SPEC-GOV-MIN-004 |
| TEST-GOV-MIN-005 | 结构 | Release Evidence 同一 PR 约定 | Change/README 文档 | SPEC-GOV-MIN-005 |
| TEST-GOV-MIN-SEC-001 | 安全 | Token 隔离与 high-risk 身份判断 | runner env、human review | SEC-GOV-MIN-001 |
| TEST-GOV-MIN-TRACE-001 | 集成 | 完整仓库和四项门禁回归 | tools/check.py | 全部 Spec |

### Spec 追踪矩阵

| Spec ID | Flow/Use Case | Rule/Invariant | Command/Contract | Test |
|---|---|---|---|---|
| SPEC-GOV-MIN-001 | FLOW-GOV-MIN-001 | SEC-GOV-MIN-001 | MODULE-GOV-MIN-001 | TEST-GOV-MIN-001、TEST-GOV-MIN-SEC-001、TEST-GOV-MIN-TRACE-001 |
| SPEC-GOV-MIN-002 | FLOW-GOV-MIN-001 | DESIGN-GOV-MIN-002 | MODULE-GOV-MIN-002 | TEST-GOV-MIN-002、TEST-GOV-MIN-TRACE-001 |
| SPEC-GOV-MIN-003 | FLOW-GOV-MIN-001 | DESIGN-GOV-MIN-003 | MODULE-GOV-MIN-003 | TEST-GOV-MIN-003、TEST-GOV-MIN-TRACE-001 |
| SPEC-GOV-MIN-004 | FLOW-GOV-MIN-001 | SEC-GOV-MIN-001 | MODULE-GOV-MIN-004 | TEST-GOV-MIN-004、TEST-GOV-MIN-SEC-001、TEST-GOV-MIN-TRACE-001 |
| SPEC-GOV-MIN-005 | FLOW-GOV-MIN-001 | MIG-GOV-MIN-001 | Release Evidence Contract | TEST-GOV-MIN-005、TEST-GOV-MIN-TRACE-001 |

## 失败、补偿与回滚

### 事务、一致性、并发与幂等

| FAIL ID | 失败点 | 系统状态 | 用户可见结果 | 补偿/重试/幂等 |
|---|---|---|---|---|
| FAIL-GOV-MIN-001 | 注册测试失败或超时 | PR 检查失败 | 输出 Change/Test 和退出原因 | 修复测试后重跑，命令执行幂等 |
| FAIL-GOV-MIN-002 | Base Capability 内容读取失败 | 精确范围校验失败关闭 | 输出资产路径和读取诊断 | GitHub API 恢复后重跑 |
| FAIL-GOV-MIN-003 | high-risk 缺少人类批准 | pr-governance 失败 | 输出需批准的 Change ID | 非作者人类批准当前 Head 后重跑 |

### 回滚方案

可分别移除注册测试 Workflow 步骤、精确范围函数、占位 ID 规则和 high-risk Profile 分支；回滚时保留现有 Codex Review、粗粒度 Change 类型和 Test Registry 结构校验，不影响历史 Change。

## 迁移方案

MIG-GOV-MIN-001：新规则从 CHG-0010 起立即适用；历史 completed Change 不重放注册命令。Release Evidence 以后绑定最终 PR Head、Repository Validation、PR Governance 和注册测试结果，不要求合入前填写 Merge SHA，也不要求额外 post-merge 收口 PR。

## 备选方案与权衡

### 非功能设计

N/A: performance - 只运行当前 PR 声明 Change 的去重命令，并为每条命令配置 300 秒默认超时，不建立独立性能预算。

### 方案权衡

| 方案 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| 执行全部历史 Change 测试 | 覆盖最完整 | CI 时间持续增长 | 不采用 |
| 完整 Diff 到 Task/Module/Spec 映射 | 追踪最细 | 维护负担和误报高 | 不采用 |
| 四项最小门禁 | 补齐关键真实性且影响有限 | 仍依赖 Review 判断语义质量 | 采用 |

### 风险

| 风险 | 影响 | 缓解措施 | Owner |
|---|---|---|---|
| 测试命令执行不可信代码 | 凭证泄露或 Runner 滥用 | 最小环境、Runner 白名单、shell=False、超时 | repository-owner |
| Capability Diff 误判 | 合法 PR 被阻断 | 按 ID 比较 Base/Head 记录并增加回归 | repository-owner |
| high-risk 无可用人类 Reviewer | 交付等待 | 只对 high-risk 生效并配置 CODEOWNERS | repository-owner |

### 开放问题

无开放问题。
