# Tasks

## TASK-GOV-009 修复 Decision 类型与历史路径范围校验
- Specs: SPEC-GOV-BOUNDARY-001
- Status: in-progress
- Depends on: none
- Tests: TEST-GOV-BOUNDARY-001, TEST-GOV-BOUNDARY-SEC-001
- Evidence: evidence/TASK-GOV-009.md
- Scope: tools/validate_pr_change.py, tools/validate_pr_change_strict.py, tools/tests/test_governance_validator_boundaries.py
- Acceptance: SCN-GOV-BOUNDARY-001-01, SCN-GOV-BOUNDARY-001-02, SCN-GOV-BOUNDARY-001-03
- Definition of Done: canonical 类型映射、Head/Base 读取、rename/delete 与 README 分类均有正反例并通过在线校验
- Rollback: 恢复原 PR 范围校验器并保留失败样例，禁止通过放宽所有 Decision 类型绕过

## TASK-GOV-010 屏蔽 strict Spec 中的 fenced 示例
- Specs: SPEC-GOV-BOUNDARY-002
- Status: in-progress
- Depends on: none
- Tests: TEST-GOV-BOUNDARY-002, TEST-GOV-BOUNDARY-SEC-001
- Evidence: evidence/TASK-GOV-010.md
- Scope: tools/validate_change_quality_strict.py, tools/tests/test_governance_validator_boundaries.py
- Acceptance: SCN-GOV-BOUNDARY-002-01
- Definition of Done: fenced 示例和未闭合围栏均不产生正式 Spec/Scenario，真实结构和追踪保持不变
- Rollback: 恢复原严格入口并停止在 Spec 中使用代码示例，直至解析修复重新上线

## TASK-GOV-011 修复 Design CommonMark 段落边界
- Specs: SPEC-GOV-BOUNDARY-003
- Status: in-progress
- Depends on: none
- Tests: TEST-GOV-BOUNDARY-003, TEST-GOV-BOUNDARY-SEC-001
- Evidence: evidence/TASK-GOV-011.md
- Scope: tools/validate_design.py, tools/tests/test_governance_validator_boundaries.py
- Acceptance: SCN-GOV-BOUNDARY-003-01, SCN-GOV-BOUNDARY-003-02
- Definition of Done: lazy quote 与带正文列表项场景行为符合 CommonMark，既不让引用 ID 漏检也不误屏蔽合法设计
- Rollback: 恢复原段落状态机并将受影响 Markdown 写法列为临时限制
