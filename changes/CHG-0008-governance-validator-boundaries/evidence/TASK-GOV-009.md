# TASK-GOV-009 Evidence

- Specs: SPEC-GOV-BOUNDARY-001
- Scenarios: SCN-GOV-BOUNDARY-001-01, SCN-GOV-BOUNDARY-001-02, SCN-GOV-BOUNDARY-001-03
- Branch: agent/governance-validator-boundaries
- Tests: TEST-GOV-BOUNDARY-001, TEST-GOV-BOUNDARY-SEC-001
- Status: implementation in progress

实现保留 GitHub changed-file 状态与 Base SHA，严格入口按 Head/Base 来源读取 Decision 元数据，并区分正式 `DEC-*.md` 与支持文档。最终 Actions Run 与 Head SHA 将在 CI 通过后补充。
