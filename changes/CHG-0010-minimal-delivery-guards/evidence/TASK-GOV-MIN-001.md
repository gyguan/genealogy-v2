# TASK-GOV-MIN-001 Evidence

- Specs: SPEC-GOV-MIN-001
- Tests: TEST-GOV-MIN-001, TEST-GOV-MIN-SEC-001, TEST-GOV-MIN-TRACE-001
- Branch: agent/minimal-delivery-guards
- Status: implementation in progress

`run_change_tests.py` 已实现当前 PR Change 解析、Runner 白名单、shell 拒绝、超时、命令去重和最小环境隔离。最终 Head、Actions Run 与注册命令结果将在 CI 通过后补充。
