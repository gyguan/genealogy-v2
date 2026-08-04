# Tasks

每个任务使用 `## TASK-xxxx`，并维护以下字段：

```markdown
## TASK-0001 可验证纵向任务
- Specs: SPEC-...
- Status: planned
- Depends on: none
- Tests: TEST-...
- Evidence: pending
- Scope: 本任务允许修改的模块或文件范围
- Acceptance: SCN-...
- Definition of Done: 可客观验证的完成条件
- Rollback: 失败时如何撤销或恢复
```

Task 应按可观察的端到端行为拆分，而不是按数据库、后端、前端等技术层机械拆分；该判断属于 Review-only。
