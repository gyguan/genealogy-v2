# Tasks

## TASK-DESIGN-V11-001 建立机器设计契约与模板
- Specs: SPEC-GOV-V11-001, SPEC-GOV-V11-002, SPEC-GOV-V11-003, SPEC-GOV-V11-005
- Status: completed
- Depends on: none
- Tests: TEST-DESIGN-V11-001, TEST-DESIGN-V11-002, TEST-DESIGN-V11-003, TEST-DESIGN-V11-SEC-001
- Evidence: evidence/TASK-DESIGN-V11-001.md
- Scope: changes/_template, tools/validate_design_machine.py, tools/new_change.py
- Acceptance: SCN-GOV-V11-001-01, SCN-GOV-V11-001-02, SCN-GOV-V11-001-03, SCN-GOV-V11-002-01, SCN-GOV-V11-002-02, SCN-GOV-V11-003-01, SCN-GOV-V11-003-02, SCN-GOV-V11-005-01, SCN-GOV-V11-005-02
- Definition of Done: 新Change生成机器契约，引用、facet、FACT/ASM/OPEN、Definition和Traceability可确定性校验
- Rollback: 移除机器校验入口并恢复模板和生成器，保留v1历史兼容

## TASK-DESIGN-V11-002 增强需求输入与Context Pack
- Specs: SPEC-GOV-V11-002, SPEC-GOV-V11-004
- Status: completed
- Depends on: TASK-DESIGN-V11-001
- Tests: TEST-DESIGN-V11-003, TEST-DESIGN-V11-004
- Evidence: evidence/TASK-DESIGN-V11-002.md
- Scope: changes/_template/proposal.md, tools/context.py, AGENTS.md
- Acceptance: SCN-GOV-V11-002-01, SCN-GOV-V11-002-02, SCN-GOV-V11-002-03, SCN-GOV-V11-004-01
- Definition of Done: Proposal包含事实来源、假设和验收边界，Context Pack只输出当前Change相关资产
- Rollback: 恢复原Proposal模板和context.py路径列表模式

## TASK-DESIGN-V11-003 分离设计生成与独立语义评审
- Specs: SPEC-GOV-V11-004
- Status: completed
- Depends on: TASK-DESIGN-V11-002
- Tests: TEST-DESIGN-V11-004, TEST-DESIGN-V11-005
- Evidence: evidence/TASK-DESIGN-V11-003.md
- Scope: skills/to-spec, skills/openspec-validation, skills/design-review, skills/README.md
- Acceptance: SCN-GOV-V11-004-01, SCN-GOV-V11-004-02
- Definition of Done: 生成、确定性验证和独立语义评审职责清晰且不可相互冒充
- Rollback: 移除design-review Skill并恢复原Skill流程

## TASK-DESIGN-V11-004 接入统一检查并完成回归测试
- Specs: SPEC-GOV-V11-001, SPEC-GOV-V11-003, SPEC-GOV-V11-005
- Status: completed
- Depends on: TASK-DESIGN-V11-001, TASK-DESIGN-V11-002, TASK-DESIGN-V11-003
- Tests: TEST-DESIGN-V11-001, TEST-DESIGN-V11-002, TEST-DESIGN-V11-003, TEST-DESIGN-V11-004, TEST-DESIGN-V11-005, TEST-DESIGN-V11-SEC-001
- Evidence: evidence/TASK-DESIGN-V11-004.md
- Scope: tools/check.py, tools/tests/test_validate_design_machine.py, changes/CHG-0008-design-contract-v1-1
- Acceptance: SCN-GOV-V11-001-02, SCN-GOV-V11-001-03, SCN-GOV-V11-003-02, SCN-GOV-V11-005-01, SCN-GOV-V11-005-02
- Definition of Done: 合法仓库通过，关键反例稳定失败，v1历史Change保持兼容
- Rollback: 从check.py移除机器校验入口并保留失败证据
