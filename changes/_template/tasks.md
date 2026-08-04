# Tasks

每个真实任务使用 `## TASK-xxxx` 标题，并维护以下机器可识别字段：

```markdown
## TASK-0001 task-title

- Specs: SPEC-DOMAIN-001
- Status: planned
- Depends on: none
- Tests: TEST-DOMAIN-001
- Evidence: evidence/TASK-0001.md
```

合法状态为 `planned`、`ready`、`in-progress`、`completed`、`blocked`、`cancelled`。每个任务还必须说明纵向实现范围、验收标准、完成定义和回滚条件。
