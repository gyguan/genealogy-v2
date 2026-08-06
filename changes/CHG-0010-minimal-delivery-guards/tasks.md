# Tasks

## TASK-GOV-MIN-001 执行当前 Change 注册测试
- Specs: SPEC-GOV-MIN-001
- Status: completed
- Depends on: none
- Tests: TEST-GOV-MIN-001, TEST-GOV-MIN-SEC-001, TEST-GOV-MIN-TRACE-001
- Evidence: evidence/TASK-GOV-MIN-001.md
- Scope: tools/run_change_tests.py, .github/workflows/validate.yml, tools/tests/test_minimal_delivery_guards.py
- Acceptance: SCN-GOV-MIN-001-01, SCN-GOV-MIN-001-02, SCN-GOV-MIN-001-03
- Definition of Done: 当前PR声明Change的注册命令被安全执行，失败、超时和凭证隔离有稳定回归
- Rollback: 移除Workflow注册测试步骤并保留Test Registry结构校验

## TASK-GOV-MIN-002 精确校验正式资产影响范围
- Specs: SPEC-GOV-MIN-002
- Status: completed
- Depends on: none
- Tests: TEST-GOV-MIN-002, TEST-GOV-MIN-TRACE-001
- Evidence: evidence/TASK-GOV-MIN-002.md
- Scope: tools/validate_pr_change_strict.py, tools/tests/test_minimal_delivery_guards.py
- Acceptance: SCN-GOV-MIN-002-01, SCN-GOV-MIN-002-02
- Definition of Done: Domain、Decision和真实变化Capability未声明时PR失败，未变化Capability不增加声明负担
- Rollback: 恢复目录级Change类型校验并保留失败样例

## TASK-GOV-MIN-003 阻断评审态模板占位 ID
- Specs: SPEC-GOV-MIN-003
- Status: completed
- Depends on: none
- Tests: TEST-GOV-MIN-003, TEST-GOV-MIN-TRACE-001
- Evidence: evidence/TASK-GOV-MIN-003.md
- Scope: tools/validate_change_quality_strict.py, tools/validate_design_machine.py, tools/tests/test_minimal_delivery_guards.py
- Acceptance: SCN-GOV-MIN-003-01, SCN-GOV-MIN-003-02
- Definition of Done: Draft生成保持可用，Review-ready的Spec、Scenario、Task、Test和机器设计占位ID稳定失败
- Rollback: 移除占位Token规则并继续依赖人工Review替换

## TASK-GOV-MIN-004 对 high-risk 增加人类批准
- Specs: SPEC-GOV-MIN-004
- Status: completed
- Depends on: none
- Tests: TEST-GOV-MIN-004, TEST-GOV-MIN-SEC-001, TEST-GOV-MIN-TRACE-001
- Evidence: evidence/TASK-GOV-MIN-004.md
- Scope: tools/validate_pr.py, .github/governance.yaml, tools/tests/test_minimal_delivery_guards.py
- Acceptance: SCN-GOV-MIN-004-01, SCN-GOV-MIN-004-02, SCN-GOV-MIN-004-03
- Definition of Done: standard/lightweight保持现有Review效率，high-risk只接受当前Head非作者人类APPROVED
- Rollback: 移除high_risk配置分支并恢复统一Codex Review规则

## TASK-GOV-MIN-005 简化 Release 单 PR 收口
- Specs: SPEC-GOV-MIN-005
- Status: completed
- Depends on: TASK-GOV-MIN-001, TASK-GOV-MIN-002, TASK-GOV-MIN-003, TASK-GOV-MIN-004
- Tests: TEST-GOV-MIN-005, TEST-GOV-MIN-TRACE-001
- Evidence: evidence/TASK-GOV-MIN-005.md
- Scope: AGENTS.md, changes/README.md, .github/PULL_REQUEST_TEMPLATE.md, changes/CHG-0010-minimal-delivery-guards
- Acceptance: SCN-GOV-MIN-005-01
- Definition of Done: Release Evidence明确绑定最终PR Head和校验结果，同一实现PR可完成completed状态，不要求Merge SHA
- Rollback: 恢复合并后手工状态收口流程
