# Repository Governance Spec Delta

## ADDED

## SPEC-GOV-001 权威来源与指令优先级

系统必须保证安全红线、正式领域不变量和已接受 Decision 不会被临时用户指令或 Skill 静默覆盖。

### 验收场景

当用户要求绕过审核或修改正式不变量时，Agent 必须要求通过独立 Change 评审，而不是直接实现。

## SPEC-GOV-002 Change 状态与追踪门禁

仓库必须自动校验 Change 类型、状态、Gate、Capability、Domain、Decision、Spec、Task 和 Evidence 的引用及一致性。

### 验收场景

当 implementing Change 的 Implementation Gate 未批准、Task 引用未知 Spec 或完成 Task 缺失 Evidence 时，仓库校验失败。

## SPEC-GOV-003 领域依赖单一事实源

领域依赖必须只维护在 `domains/context-map.yaml`，依赖需要类型、目标有效且无环。

### 验收场景

当领域 Frontmatter 重复声明依赖、依赖未知领域或出现循环时，仓库校验失败。

## SPEC-GOV-004 渐进式代码布局

首期代码必须按领域对齐的模块化单体布局演进，不预建空目录，不允许无 Decision 的泛化共享目录。

### 验收场景

首个业务实现 Change 可以依据 Accepted Decision 创建最小必要的 `apps/`、`modules/`、`platform/`、`contracts/` 和 `tests/` 目录。
