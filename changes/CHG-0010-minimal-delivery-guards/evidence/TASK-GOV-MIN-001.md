# TASK-GOV-MIN-001 Evidence

- Specs: SPEC-GOV-MIN-001
- Tests: TEST-GOV-MIN-001, TEST-GOV-MIN-SEC-001, TEST-GOV-MIN-TRACE-001
- Implementation baseline: `0ad5509a021be5862746fc1530484dbaf4a0e76b`
- Repository Validation Run: `30977322275`
- Result: success

`run_change_tests.py` 已实现当前 PR Change 解析、Runner 白名单、shell 拒绝、超时、命令去重、最小环境隔离和 checkout 凭证禁用。Run `30977322275` 真实执行了 CHG-0010 注册命令并通过；最终 Head 与最终 Required Checks 绑定记录在 PR #19 Body。
