# Repository Governance Spec Delta

## ADDED

## SPEC-GOV-V11-001 机器设计契约必须成为确定性事实源
#### Requirement
从 CHG-0008 起，每个 Change 必须声明 `design_machine_contract_version: 1` 并维护 `design.yaml`，其引用、facet、事实、假设、开放问题、定义和追踪必须可确定性校验。
#### Scenario SCN-GOV-V11-001-01 生成机器契约
- Given: 使用 `tools/new_change.py` 创建 CHG-0008 及以后的新 Change
- When: 生成器完成初始化
- Then: Change 声明机器契约版本并生成与正式范围一致的 `design.yaml`
#### Scenario SCN-GOV-V11-001-02 缺失机器契约
- Given: 新 Change 缺少版本或 `design.yaml`
- When: 执行统一检查
- Then: 校验返回非零并指出缺失资产
#### Scenario SCN-GOV-V11-001-03 历史兼容
- Given: CHG-0001 至 CHG-0007 不使用机器契约
- When: 执行统一检查
- Then: 历史 Change 继续按原契约通过

## SPEC-GOV-V11-002 设计事实、假设与开放问题必须显式区分
#### Requirement
机器契约必须区分有来源的 FACT、显式状态的 ASM 和有负责人及阻断性的 OPEN，不得将 AI 推断静默作为正式事实。
#### Scenario SCN-GOV-V11-002-01 事实有来源
- Given: FACT 声明支持结论的正式来源
- When: 执行机器契约校验
- Then: 事实来源检查通过
#### Scenario SCN-GOV-V11-002-02 阻断假设未确认
- Given: review-ready Change 仍有 blocking 且 proposed 的 ASM
- When: 执行机器契约校验
- Then: 校验失败并阻止 Spec Gate
#### Scenario SCN-GOV-V11-002-03 批准态存在开放问题
- Given: 已批准 Design 仍包含 OPEN
- When: 执行机器契约校验
- Then: 校验失败

## SPEC-GOV-V11-003 Facet 必须经过主动判断
#### Requirement
生成器应根据 Change 类型预置确定必需项，并将不确定项标记为 `review-required`；进入 review 前所有 facet 必须收敛为 required 或 not-applicable。
#### Scenario SCN-GOV-V11-003-01 类型化初始化
- Given: 创建 product、domain、engineering、governance 或 security Change
- When: 生成机器契约
- Then: 安全、模块和测试项按策略初始化，其他不确定项保持 review-required
#### Scenario SCN-GOV-V11-003-02 未完成判断
- Given: Change 进入 review 但仍有 review-required
- When: 执行机器契约校验
- Then: 校验失败并指出具体 facet

## SPEC-GOV-V11-004 AI 必须读取最小 Context Pack 并接受独立设计评审
#### Requirement
`context.py --bundle` 必须输出当前 Change 的精确 Capability、Domain、Decision、全局约束和机器设计输入；设计完成后由独立 `design-review` Skill 进行语义挑战。
#### Scenario SCN-GOV-V11-004-01 输出 Context Pack
- Given: Change 引用正式资产
- When: 执行 `python tools/context.py <CHG-ID> --bundle`
- Then: 输出可机器读取的最小上下文和来源路径
#### Scenario SCN-GOV-V11-004-02 独立语义评审
- Given: Proposal、Spec 和 Design 已完成确定性检查
- When: 独立上下文执行 design-review
- Then: 按 Error、Warning、Review-only 挑战语义且不冒充生成 Agent 自检

## SPEC-GOV-V11-005 机器追踪必须与正式 Test 注册表一致
#### Requirement
`design.yaml` 中的 Definition 与 Traceability 必须引用真实 Spec/Test，且 Traceability 中的 Test 必须在 `tests.yaml` 中覆盖对应 Spec。
#### Scenario SCN-GOV-V11-005-01 追踪完整
- Given: 每个 Spec 有定义与注册测试覆盖
- When: 执行机器契约校验
- Then: 追踪检查通过
#### Scenario SCN-GOV-V11-005-02 追踪虚构或错配
- Given: Definition 或 Traceability 引用未知 Test，或 Test 未覆盖对应 Spec
- When: 执行机器契约校验
- Then: 校验失败并定位引用
