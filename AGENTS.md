# AI 与贡献者规则

本仓库的产品资产和后续代码主要由 AI 生成。所有 Agent 和贡献者必须遵守本文件。

## 必读顺序

1. 根 `AGENTS.md`；
2. 当前 `changes/<change-id>/change.yaml` 和 `proposal.md`；
3. 受影响的 `domains/*.md`、`domains/glossary.yaml` 和 `domains/context-map.yaml`；
4. 相关 `decisions/`；
5. 本次使用的 `skills/<skill>/SKILL.md`。

## 指令优先级

```text
用户当前明确要求
> AGENTS.md
> 当前 Change
> 正式领域资产与已接受 Decision
> 项目 Skill
> 其他参考材料
```

## Change 要求

非平凡需求必须创建 `changes/CHG-xxxx-name/`，至少包含：

- `change.yaml`：唯一状态和 Gate；
- `proposal.md`：背景、目标、非目标、范围和修改边界；
- `specs/`：按领域维护的 Spec Delta；
- `design.md`：方案、权衡、测试 Seam 和风险；
- `tasks.md`：纵向任务、测试和完成定义；
- `evidence/`：验证、评审和测试证据。

GitHub Issue 是执行视图，批准后的 Change Spec 才是需求事实源。

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

必须证明目标和非目标得到满足、领域不变量未被破坏、Spec/Task/代码/测试可追踪、正例反例边界案例通过、隐私与安全检查通过、双轴评审无阻断问题。
