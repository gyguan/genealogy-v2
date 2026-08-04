# Repository Governance Spec Delta

## ADDED

## SPEC-GOV-DESIGN-001 新 Change 必须使用设计契约
#### Requirement
从 CHG-0007 起，每个 Change 必须声明 `design_contract_version: 1`，并在 `design.md` 中维护机器可读 Frontmatter 和八个固定设计章节。
#### Scenario SCN-GOV-DESIGN-001-01 生成设计契约
- Given: 使用 `tools/new_change.py` 创建 CHG-0007 及以后的新 Change
- When: 生成器完成文件初始化
- Then: Change 元数据和 Design Frontmatter 均包含设计契约版本及正式范围引用
#### Scenario SCN-GOV-DESIGN-001-02 缺少契约版本
- Given: CHG-0007 及以后的 Change 缺少有效设计契约版本
- When: 执行统一仓库检查
- Then: 设计校验返回非零并指出缺少整数版本 1
#### Scenario SCN-GOV-DESIGN-001-03 历史兼容
- Given: CHG-0001 至 CHG-0006 未声明设计契约版本
- When: 执行统一仓库检查
- Then: 历史 Change 不因新设计契约边界被拒绝

## SPEC-GOV-DESIGN-002 设计引用必须与正式资产一致
#### Requirement
Design 中的 Change、Capability、Spec、Domain 和 Decision 引用必须与 `change.yaml` 和 Spec 文件完全一致。
#### Scenario SCN-GOV-DESIGN-002-01 引用一致
- Given: Design 引用集合与正式资产一致
- When: 执行设计校验
- Then: 引用一致性检查通过
#### Scenario SCN-GOV-DESIGN-002-02 引用不一致
- Given: Design 缺失、多出或写错任一正式资产引用
- When: 执行设计校验
- Then: 校验返回非零并指出不一致字段

## SPEC-GOV-DESIGN-003 适用性与稳定 ID 必须可校验
#### Requirement
每个设计 facet 必须标记为 `required` 或 `not-applicable`；required 必须使用约定前缀的稳定 ID，not-applicable 必须在对应章节给出具体原因。
#### Scenario SCN-GOV-DESIGN-003-01 适用性完整
- Given: required 项有稳定 ID 且不适用项有非空原因
- When: 执行设计校验
- Then: applicability 检查通过
#### Scenario SCN-GOV-DESIGN-003-02 适用性缺失
- Given: facet 缺失、状态未知、required 缺少 ID 或 N/A 缺少原因
- When: 执行设计校验
- Then: 校验返回非零并指出具体 facet

## SPEC-GOV-DESIGN-004 设计必须形成 Spec 与测试追踪
#### Requirement
每个 Spec 必须进入测试追踪矩阵；Rule、Invariant、Command、Constraint 和安全定义必须关联所需的真实 Spec/Test。
#### Scenario SCN-GOV-DESIGN-004-01 追踪完整
- Given: Spec 矩阵、规则行和测试注册表引用完整且真实存在
- When: 执行设计校验
- Then: 追踪检查通过
#### Scenario SCN-GOV-DESIGN-004-02 追踪缺失
- Given: 任一 Spec 未进入矩阵或定义行引用缺失、虚构的 Spec/Test
- When: 执行设计校验
- Then: 校验返回非零并定位缺失或未知引用

## SPEC-GOV-DESIGN-005 Spec Gate 必须阻断未完成设计
#### Requirement
进入 Review 后，Design 不得残留模板注释、TODO、TBD、待确认或待补充；批准 Spec Gate 前开放问题必须为零，且代码块或空结构不得伪装成有效设计。
#### Scenario SCN-GOV-DESIGN-005-01 完成设计
- Given: 设计章节有真实内容、开放问题为零且无占位文本
- When: Spec Gate 进入 approved
- Then: 设计完整性检查通过
#### Scenario SCN-GOV-DESIGN-005-02 未完成设计
- Given: Design 存在占位文本、空 Frontmatter、伪章节或未关闭 OPEN 项
- When: 执行设计校验
- Then: 校验返回非零并阻止 Spec Gate
