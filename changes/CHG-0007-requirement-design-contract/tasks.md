# Tasks

## TASK-DESIGN-001 升级 Change 与 Design 模板
- Specs: SPEC-GOV-DESIGN-001, SPEC-GOV-DESIGN-002, SPEC-GOV-DESIGN-003
- Status: completed
- Depends on: none
- Tests: TEST-DESIGN-001, TEST-DESIGN-002, TEST-DESIGN-003, TEST-DESIGN-004
- Evidence: evidence/TASK-DESIGN-001.md
- Scope: changes/_template, tools/new_change.py, changes/README.md
- Acceptance: SCN-GOV-DESIGN-001-01, SCN-GOV-DESIGN-001-02, SCN-GOV-DESIGN-001-03, SCN-GOV-DESIGN-002-01, SCN-GOV-DESIGN-002-02, SCN-GOV-DESIGN-003-01, SCN-GOV-DESIGN-003-02
- Definition of Done: 模板和生成器同时初始化 strict Change 与 Design Contract v1，引用和适用性反例稳定失败
- Rollback: 恢复主分支原模板与生成器，保留已生成 Change 数据并停止新增契约

## TASK-DESIGN-002 强化 AI 设计指令与 Skill
- Specs: SPEC-GOV-DESIGN-003, SPEC-GOV-DESIGN-004, SPEC-GOV-DESIGN-005
- Status: completed
- Depends on: TASK-DESIGN-001
- Tests: TEST-DESIGN-004, TEST-DESIGN-005, TEST-DESIGN-006, TEST-DESIGN-SEC-001, TEST-DESIGN-SEC-002
- Evidence: evidence/TASK-DESIGN-002.md
- Scope: AGENTS.md, skills/to-spec, skills/openspec-validation, .github/PULL_REQUEST_TEMPLATE.md
- Acceptance: SCN-GOV-DESIGN-003-01, SCN-GOV-DESIGN-003-02, SCN-GOV-DESIGN-004-01, SCN-GOV-DESIGN-004-02, SCN-GOV-DESIGN-005-01, SCN-GOV-DESIGN-005-02
- Definition of Done: AI 指令、Skill、PR 模板与确定性门禁表达一致且保留 Review-only 判断边界
- Rollback: 恢复规则入口并保留设计校验器为独立试验工具

## TASK-DESIGN-003 实现设计契约校验与反例测试
- Specs: SPEC-GOV-DESIGN-001, SPEC-GOV-DESIGN-002, SPEC-GOV-DESIGN-003, SPEC-GOV-DESIGN-004, SPEC-GOV-DESIGN-005
- Status: completed
- Depends on: TASK-DESIGN-001
- Tests: TEST-DESIGN-001, TEST-DESIGN-002, TEST-DESIGN-003, TEST-DESIGN-004, TEST-DESIGN-005, TEST-DESIGN-006, TEST-DESIGN-SEC-001, TEST-DESIGN-SEC-002
- Evidence: evidence/TASK-DESIGN-003.md
- Scope: tools/validate_design.py, tools/_validate_design_core.py, tools/check.py, tools/tests/test_validate_design*.py
- Acceptance: SCN-GOV-DESIGN-001-01, SCN-GOV-DESIGN-001-02, SCN-GOV-DESIGN-001-03, SCN-GOV-DESIGN-002-01, SCN-GOV-DESIGN-002-02, SCN-GOV-DESIGN-003-01, SCN-GOV-DESIGN-003-02, SCN-GOV-DESIGN-004-01, SCN-GOV-DESIGN-004-02, SCN-GOV-DESIGN-005-01, SCN-GOV-DESIGN-005-02
- Definition of Done: 合法仓库通过，关键 Markdown、YAML、引用和追踪绕过均有回归测试且统一检查通过
- Rollback: 从 tools/check.py 移除设计校验入口并恢复模板，不删除失败证据

## TASK-DESIGN-004 完成评审、证据与发布闭环
- Specs: SPEC-GOV-DESIGN-005
- Status: completed
- Depends on: TASK-DESIGN-002, TASK-DESIGN-003
- Tests: TEST-DESIGN-001, TEST-DESIGN-006, TEST-DESIGN-SEC-001
- Evidence: evidence/TASK-DESIGN-004.md
- Scope: changes/CHG-0007-requirement-design-contract/evidence, PR-9
- Acceptance: SCN-GOV-DESIGN-005-01, SCN-GOV-DESIGN-005-02
- Definition of Done: 最终 Head 的 CI、独立 Review、Thread、Gate、Task 和 Evidence 一致并合入 main
- Rollback: 任一阻断 Review、未解决 Thread 或检查失败时停止合入
