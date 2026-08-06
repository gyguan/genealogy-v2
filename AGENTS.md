# AI 与贡献者规则

本仓库主要由 AI 辅助生成，所有 Agent 与贡献者必须遵守本文件。

## 最小读取顺序

1. `AGENTS.md` 与 `SECURITY.md`；
2. 当前 Change 的 `change.yaml`、`proposal.md`；
3. 运行 `python tools/context.py <CHG-ID> --bundle`，优先读取最小 Context Pack；
4. 当前 Change 的 `design.yaml`、相关 Spec 和本次使用的 Skill；
5. 只有在 Context Pack 信息不足时，才打开完整 Capability、Domain 或 Decision 原文。

不得默认加载全部 Capability。`product/capability-map.yaml` 只保存 Manifest，正式能力唯一来源是 `product/capabilities/*.yaml`。

## 指令优先级
平台安全、法律与合规 > SECURITY 与全局红线 > 正式领域不变量与 Accepted Decision > 已批准 Change > 用户边界内要求 > Skill > 参考材料。

## Change 与效率
- 风险控制与 Change Profile 匹配：lightweight、standard、high-risk；
- 产品、领域、安全必须 high-risk；治理不得 lightweight；
- 使用 `new_change.py` 参数化生成，不手工复制模板；
- 新 Change 默认使用 `quality_policy: strict`，并维护 `tests.yaml`；
- PR 中只执行 Body 明确声明 Change 的注册测试，不重放全部历史 Change；
- Task 按可验证纵向行为拆分，使用最少可独立交付切片；
- 统一执行 `python tools/check.py`。

## 诊断与评审边界
- Error 只用于客观、确定、可重复判断的错误，并阻断检查；
- Warning 用于启发式风险和历史格式迁移，不直接替代 Reviewer 决策；
- Review-only 用于业务正确性、领域语义、方案取舍、风险接受和测试充分性；
- 不得为了自动化而让 Python、规则扫描或 LLM 自动裁决 Review-only 问题；
- Warning 必须在评审中解决或明确接受；lightweight、standard 保持当前 Head Codex Review，high-risk 还必须获得非作者人类在当前 Head 的 APPROVED。

## 需求设计契约
- `CHG-0007` 起继续维护 Design Contract v1 的 `design.md` Frontmatter 与八个固定章节；
- `CHG-0009` 起还必须声明 `design_machine_contract_version: 1` 并维护 `design.yaml`；
- `design.yaml` 是引用、适用性、事实、假设、开放问题、稳定设计 ID 和 Spec/Test 追踪的机器事实源；`design.md` 负责解释流程、模型、失败、风险和取舍；
- Design 的 Change、Capability、Spec、Domain 和 Decision 引用必须与正式资产完全一致；
- 开始设计前先记录已确认事实 `FACT-...`、显式假设 `ASM-...` 和开放问题 `OPEN-...`；不得把 AI 推断静默写成业务事实；
- 每个 facet 初始可以是 `review-required`，但进入 review 或批准 Spec Gate 前必须收敛为 `required` 或 `not-applicable`；
- `required` 必须给出原因和稳定设计 ID；`not-applicable` 必须给出具体原因；
- 业务规则、不变量、命令、约束和安全定义必须追踪到正式 Spec/Test；每个 Spec 必须进入 `design.yaml.traceability`；
- 阻断假设未确认、存在开放问题、残留 TODO/TBD/待确认、模板占位 ID 或引用不一致时，不得进入评审态；
- 设计不得静默修改领域不变量、Accepted Decision、产品范围或安全红线；需要修改时必须建立独立 Change；
- `tools/validate_design.py`、`tools/validate_design_machine.py` 与 `tools/check.py` 是确定性门禁，Skill 或人工判断不得绕过。

## 生成与评审分离
- `to-spec` 负责生成 Proposal、Spec、`design.yaml` 和 `design.md`；
- `openspec-validation` 负责完整性与确定性一致性检查；
- `design-review` 必须由独立上下文执行，重点挑战需求理解、领域语义、遗漏、过度设计、安全和测试充分性；
- 生成 Agent 不得把自己的解释当成独立评审结论。

## 产品规划纪律
- Release 事实源为 `product/releases.yaml`；Capability 唯一事实源为分组文件；
- Capability 责任不等同代码归属；依赖不得循环或版本倒挂；
- 处于 `detailed` 或 `bounded` 规划深度的实施版本必须声明来源、审核、查询、迁出与恢复闭环；首个实施版本之后还必须声明授权闭环；
- 版本与 Capability 调整必须通过产品 Change。

## 评审与合入
- 当前 Head SHA 必须获得独立 Review；新提交后旧 Review 失效；
- 触发 Codex 时使用精确命令 `@codex review <40位Head SHA>`；若 Codex 仅以 👍 表示无意见，该反应必须发生在这条服务器记录的 Head 绑定命令之后；
- 所有有效 Review Thread 必须解决或明确接受；
- PR 修改正式 Domain、Decision 或 Capability 时，实际变化 ID 必须在 Change 影响范围中声明；
- Gate 记录来源、引用、审批人和证据；
- Release Evidence 绑定最终 PR Head、Repository Validation、PR Governance 和注册测试结果，不要求合入前填写尚未产生的 Merge SHA；满足条件后可在同一个实现 PR 中更新 completed；
- CI 通过不替代 Standards/Spec 双轴评审；
- 合入前运行 `python tools/check.py`。

## 全局红线
- 不复制旧系统业务代码、表结构或兼容层；
- 不混淆自然人、姓名、家庭角色和谱系归属；
- 不混淆血缘、家庭、法律、抚养、谱籍和祭祀承继；
- 不以展示结果反推业务事实，不绕过审核写正式事实；
- 不使用万能关系模型，不删除或降低测试与验收；
- 不提交真实族人敏感信息。
