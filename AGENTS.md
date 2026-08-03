# AI 与贡献者全局规则

本仓库的设计资产和后续代码主要由 AI 生成。任何 Agent 或贡献者都必须遵守以下规则。

## 必读顺序

1. 根 `AGENTS.md`；
2. `ai/repo-map.yaml`；
3. 当前 `changes/active/<change-id>/context.yaml`；
4. 受影响领域的权威资产；
5. 相关决策、示例和 Eval。

## 指令优先级

```text
用户明确要求
> 根 AGENTS.md
> 当前 Change context.yaml
> 领域规则与正式决策
> 项目适配 Skill
> 上游 Skill
> reference/ 中的参考材料
```

上游 Skill 与本仓规则冲突时，以本仓规则为准。

## Agent Skills

- Issue 以 GitHub Issues 跟踪，具体规则见 `docs/agents/issue-tracker.md`。
- 领域语言和决策读取规则见 `docs/agents/domain.md`。
- 需求开发路由见 `docs/agents/skill-routing.md`。
- 项目适配 Skill 位于 `skills/engineering/`，禁止用上游同名 Skill 覆盖。

## 全局红线

- 不复制旧系统业务代码、表结构或兼容层。
- 不混淆自然人身份、姓名、家庭角色和谱系归属。
- 不混淆血缘、家庭、法律、抚养、谱籍和祭祀承继关系。
- 不以谱书展示结果反推正式业务事实。
- 不绕过审核直接写入正式族谱事实。
- 不把研究材料、示例或未批准 Change 当成正式需求。
- 不引入无法建立约束的万能关系或弱多态核心关联。
- 不降低、删除或绕过 Eval 和验收标准来完成任务。
- 不在仓库提交真实族人的敏感个人信息。
- 不手工修改自动生成资产。

## 需求开发纪律

- 需求存在重要歧义时，先运行 `grill-with-docs`。
- 新术语或领域边界必须通过 `domain-modeling` 固化。
- 非平凡需求必须由 `to-spec` 形成 OpenSpec Change。
- 实现任务必须由 `to-tickets` 拆为可独立验证的纵向切片。
- 编码应在预先约定的测试 Seam 上执行 TDD。
- 实现完成后必须执行 Standards 与 Spec 双轴代码评审。
- GitHub Issue 是执行视图，`changes/` 中批准的 Spec 才是需求事实源。

## 变更要求

非平凡变更必须有独立 Change 目录，并至少包含：

- `context.yaml`
- `proposal.md`
- `specs/`
- `design.md`
- `tasks.md`
- `validation/`

进入编码前还必须形成 `implementation/` 开发任务包。

## 完成定义

AI 不得仅以“已生成文件”作为完成依据。必须证明：

- 任务目标和非目标得到满足；
- 领域不变量未被破坏；
- 契约、实现与验证保持一致；
- 正例、反例和边界案例通过；
- 每个任务、代码变更和测试结果可追踪；
- Standards 与 Spec 双轴评审无阻断问题。
