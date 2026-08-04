# Tasks

## TASK-GOV-006 实现三级诊断内核
- Specs: SPEC-GOV-007
- Status: completed
- Depends on: none
- Tests: TEST-GOV-DIAGNOSTICS-001
- Evidence: evidence/TASK-GOV-006.md
- Scope: tools/diagnostics.py 与诊断报告出口
- Acceptance: SCN-GOV-007-01, SCN-GOV-007-02
- Definition of Done: Error、Warning、Review-only 可独立统计和渲染，只有 Error 返回失败退出码
- Rollback: 从 tools/check.py 移除新校验入口并删除诊断模块

## TASK-GOV-007 实现 strict Change 内容与追踪校验
- Specs: SPEC-GOV-008
- Status: completed
- Depends on: TASK-GOV-006
- Tests: TEST-GOV-QUALITY-001
- Evidence: evidence/TASK-GOV-007.md
- Scope: Change 模板、内容解析、Spec/Task/Test 双向追踪
- Acceptance: SCN-GOV-008-01, SCN-GOV-008-02
- Definition of Done: strict Change 缺失客观必填项时失败，历史 Change 仅输出迁移 Warning
- Rollback: 移除 validate_change_quality.py 入口并保留 quality_policy 元数据

## TASK-GOV-008 实现 PR Change 范围校验
- Specs: SPEC-GOV-009
- Status: completed
- Depends on: TASK-GOV-006
- Tests: TEST-GOV-PR-SCOPE-001
- Evidence: evidence/TASK-GOV-008.md
- Scope: PR 正文 Change 解析、Changed Files 分类和 Issue 真实性校验
- Acceptance: SCN-GOV-009-01, SCN-GOV-009-02
- Definition of Done: PR 声明缺失、Change 未声明或路径类型越界时返回 Error
- Rollback: 从 GitHub Actions 移除 validate_pr_change.py 步骤
