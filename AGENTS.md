# AI 与贡献者规则

本仓库主要由 AI 辅助生成，所有 Agent 与贡献者必须遵守本文件。

## 最小读取顺序

1. `AGENTS.md` 与 `SECURITY.md`；
2. 当前 Change 的 `change.yaml`、`proposal.md`；
3. 运行 `python tools/context.py <CHG-ID>`，只读取输出的版本、Capability、领域和 Decision；
4. 本次使用的 Skill。

不得默认加载全部 Capability。`product/capability-map.yaml` 只保存 Manifest，正式能力唯一来源是 `product/capabilities/*.yaml`。

## 指令优先级
平台安全、法律与合规 > SECURITY 与全局红线 > 正式领域不变量与 Accepted Decision > 已批准 Change > 用户边界内要求 > Skill > 参考材料。

## Change 与效率
- 风险控制与 Change Profile 匹配：lightweight、standard、high-risk；
- 产品、领域、安全必须 high-risk；治理不得 lightweight；
- 使用 `new_change.py` 参数化生成，不手工复制模板；
- 新 Change 默认使用 `quality_policy: strict`，并维护 `tests.yaml`；
- Task 按可验证纵向行为拆分，使用最少可独立交付切片；
- 统一执行 `python tools/check.py`。

## 诊断与评审边界
- Error 只用于客观、确定、可重复判断的错误，并阻断检查；
- Warning 用于启发式风险和历史格式迁移，不直接替代 Reviewer 决策；
- Review-only 用于业务正确性、领域语义、方案取舍、风险接受和测试充分性；
- 不得为了自动化而让 Python、规则扫描或 LLM 自动裁决 Review-only 问题；
- Warning 必须在评审中解决或明确接受，高风险 Change 仍需独立人类 APPROVED。

## 需求设计契约
- 从 `CHG-0007` 起，所有 Change 必须声明 `design_contract_version: 1`，并使用 `changes/_template/design.md`；
- Design Frontmatter 的 Change、Capability、Spec、Domain 和 Decision 必须与正式资产完全一致；
- 先判定 `applicability`：`required` 必须使用稳定 ID 给出可测试设计，`not-applicable` 必须写明 `N/A: <facet> - <具体原因>`；
- 设计必须保留八个固定章节，不得用自由格式文档替代；
- 业务规则和不变量必须同时追踪到 Spec 与 Test；每个 Spec 必须进入测试追踪矩阵；
- `open_questions > 0`、残留 TODO/TBD/待确认或设计引用不一致时，不得批准 Spec Gate；
- 设计不得静默修改领域不变量、Accepted Decision、产品范围或安全红线；需要修改时必须建立独立 Change；
- `tools/validate_design.py` 与 `tools/check.py` 是确定性门禁，Skill 或人工判断不得绕过。

## 产品规划纪律
- Release 事实源为 `product/releases.yaml`；Capability 唯一事实源为分组文件；
- Capability 责任不等同代码归属；依赖不得循环或版本倒挂；
- 处于 `detailed` 或 `bounded` 规划深度的实施版本必须声明来源、审核、查询、迁出与恢复闭环；首个实施版本之后还必须声明授权闭环；
- 版本与 Capability 调整必须通过产品 Change。

## 评审与合入
- 当前 Head SHA 必须获得独立 Review；新提交后旧 Review 失效；
- 触发 Codex 时使用精确命令 `@codex review <40位Head SHA>`；若 Codex 仅以 👍 表示无意见，该反应必须发生在这条服务器记录的 Head 绑定命令之后；
- 所有有效 Review Thread 必须解决或明确接受；
- Gate 记录来源、引用、审批人和证据；
- CI 通过不替代 Standards/Spec 双轴评审；
- 合入前运行 `python tools/check.py`。

## 全局红线
- 不复制旧系统业务代码、表结构或兼容层；
- 不混淆自然人、姓名、家庭角色和谱系归属；
- 不混淆血缘、家庭、法律、抚养、谱籍和祭祀承继；
- 不以展示结果反推业务事实，不绕过审核写正式事实；
- 不使用万能关系模型，不删除或降低测试与验收；
- 不提交真实族人敏感信息。
