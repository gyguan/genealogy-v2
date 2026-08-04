# AI 与贡献者规则

本仓库的产品资产和后续代码主要由 AI 生成。所有 Agent 和贡献者必须遵守本文件。

## 必读顺序

1. 根 `AGENTS.md` 与 `SECURITY.md`；
2. 当前 `changes/<change-id>/change.yaml` 和 `proposal.md`；
3. `domains/context-map.yaml`、受影响的 `domains/*.md` 与 `domains/glossary.yaml`；
4. 相关 `decisions/`；
5. 本次使用的 `skills/<skill>/SKILL.md`。

## 指令优先级

```text
平台安全、法律与合规约束
> SECURITY.md 与本文件全局红线
> 正式领域不变量与已接受 Decision
> 已批准 Change 的范围、约束与 Gate
> 用户在上述边界内的当前要求
> 项目 Skill
> 其他参考材料
```

用户可以提出修改领域规则、Decision 或治理规则，但不得在同一次实现任务中静默绕过。此类修改必须建立独立 Change，经评审批准后再生效。

## 权威来源

- `product/capability-map.yaml`：产品能力事实源；
- `domains/glossary.yaml`：统一业务术语事实源；
- `domains/*.md`：领域职责、非职责与不变量事实源；
- `domains/context-map.yaml`：领域依赖关系唯一事实源，领域文件不得重复声明依赖；
- `changes/<change-id>/`：单次增量需求、设计、任务与证据事实源；
- `decisions/DEC-*.md`：长期有效决策事实源；
- `skills/`：执行方法，不得覆盖正式产品、领域、Change 或 Decision。

## Change 要求

非平凡需求必须创建 `changes/CHG-xxxx-name/`，至少包含：

- `change.yaml`：唯一类型、状态、关联资产和 Gate；
- `proposal.md`：背景、目标、非目标、范围和修改边界；
- `specs/`：按领域维护的 Spec Delta；
- `design.md`：方案、权衡、测试 Seam 和风险；
- `tasks.md`：纵向任务、测试和完成定义；
- `evidence/`：验证、评审和测试证据。

GitHub Issue 是执行视图，批准后的 Change Spec 才是需求事实源。Change 状态必须与 Gate、Task 和 Evidence 一致，并通过 `tools/validate_repo.py` 校验。

## 开发纪律

- 重要歧义先使用 `grill-with-docs`。
- 新术语或领域边界通过 `domain-modeling` 固化。
- 需求通过 `to-spec` 形成 OpenSpec，并经人工评审后再实现。
- `to-tickets` 将需求拆成可独立验证的纵向切片。
- 编码在批准的测试 Seam 上执行 TDD。
- 完成后执行 Standards 与 Spec 双轴评审。
- 合入前运行 `python tools/validate_repo.py`。

## 全局红线

- 不复制旧系统业务代码、表结构或兼容层。
- 不混淆自然人身份、姓名、家庭角色和谱系归属。
- 不混淆血缘、家庭、法律、抚养、谱籍和祭祀承继关系。
- 不以谱书展示结果反推正式业务事实。
- 不绕过审核直接写入正式族谱事实。
- 不把研究材料、示例或未批准 Change 当成正式需求。
- 不引入无法建立约束的万能关系模型。
- 不通过删除、降低或绕过测试和验收标准完成任务。
- 不提交真实族人的敏感个人信息。

## 完成定义

必须证明目标和非目标得到满足、领域不变量未被破坏、Capability/Spec/Task/代码/测试/Evidence 可追踪、正例反例边界案例通过、隐私与安全检查通过、双轴评审无阻断问题。
