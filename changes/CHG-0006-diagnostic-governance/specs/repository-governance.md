# Repository Governance Spec Delta

## ADDED

## SPEC-GOV-007 三级诊断模型
#### Requirement
仓库校验必须将结果分类为 Error、Warning 和 Review-only，且只有 Error 能产生非零退出码。
#### Scenario SCN-GOV-007-01 Error 阻断
- Given: 校验发现一个客观且确定的规则错误
- When: 校验脚本完成执行
- Then: 报告包含 Error 且进程返回非零退出码
#### Scenario SCN-GOV-007-02 Warning 不阻断
- Given: 校验发现一个需要评审确认的疑似风险
- When: 报告中不存在 Error
- Then: 报告包含 Warning 且进程返回零退出码

## SPEC-GOV-008 严格 Change 内容与追踪
#### Requirement
启用 quality_policy: strict 的活动 Change 必须具备有效 Proposal、Design、结构化 Spec Scenario、Task 覆盖和测试注册表。
#### Scenario SCN-GOV-008-01 缺失场景失败
- Given: strict Change 的某个 Spec 没有可识别 Scenario
- When: 执行统一仓库检查
- Then: 校验以 Error 报告该缺失并阻断
#### Scenario SCN-GOV-008-02 历史 Change 兼容
- Given: 历史活动 Change 未启用 strict 策略
- When: 执行统一仓库检查
- Then: 新格式缺失以迁移 Warning 报告而不直接阻断

## SPEC-GOV-009 PR Change 范围约束
#### Requirement
Pull Request 必须声明至少一个真实 Change，实际修改文件必须由声明 Change 的类型覆盖，修改其他 Change 资产时必须显式声明。
#### Scenario SCN-GOV-009-01 范围匹配
- Given: governance Change 修改 tools 和 GitHub workflow
- When: 执行 PR Change 校验
- Then: 路径范围校验通过
#### Scenario SCN-GOV-009-02 范围越界
- Given: 仅声明 governance Change 却修改 product 资产
- When: 执行 PR Change 校验
- Then: 校验以 Error 阻断
