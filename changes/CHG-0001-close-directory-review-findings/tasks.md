# Tasks

## TASK-0001 修正规则与权威来源

- Specs: SPEC-GOV-001
- Status: completed
- Depends on: none
- Tests: TEST-GOV-001
- Evidence: evidence/TASK-0001.md

### 纵向实现范围

更新 README 与 AGENTS，明确不可静默覆盖的优先级和单一事实源。

### 验收标准

用户临时要求不能覆盖安全红线、领域不变量或 Accepted Decision。

### 完成定义

规则文本与 Change 流程一致，校验入口明确。

### 回滚条件

出现与平台安全约束冲突时回滚并重新评审。

## TASK-0002 完善领域、产品和 Decision 基线

- Specs: SPEC-GOV-003, SPEC-GOV-004
- Status: completed
- Depends on: TASK-0001
- Tests: TEST-GOV-002
- Evidence: evidence/TASK-0002.md

### 纵向实现范围

填充 Capability、Glossary、Typed Context Map，更新领域文件并建立代码布局 Decision。

### 验收标准

ID 唯一、引用有效、依赖无环且领域文件不重复依赖。

### 完成定义

六个领域均可由 AI 一次定位其职责、核心术语和依赖类型。

### 回滚条件

依赖方向与后续领域评审冲突时通过新 Change 调整。

## TASK-0003 建立 Change 状态与追踪校验

- Specs: SPEC-GOV-002
- Status: completed
- Depends on: TASK-0001, TASK-0002
- Tests: TEST-GOV-003
- Evidence: evidence/TASK-0003.md

### 纵向实现范围

升级 Change/Decision 模板、创建工具和仓库校验器，校验 Gate、状态、Spec、Task、Evidence、Capability、Decision 和依赖。

### 验收标准

正向样本通过，关键反例失败。

### 完成定义

本地和 GitHub Actions 共用同一校验入口。

### 回滚条件

校验器产生不可接受的误报且无法通过小范围修复解决。
