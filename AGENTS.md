# AI 与贡献者全局规则

本仓库的设计资产和后续代码主要由 AI 生成。任何 Agent 或贡献者都必须遵守本文件。

## 必读顺序

1. 根 `AGENTS.md`；
2. `ai/repo-map.yaml`；
3. 当前 Change 的 `change.yaml` 和 `context.md`；
4. 受影响领域的 `manifest.yaml`、模型、规则和 Eval；
5. 相关 Decision、接口契约和工程知识。

## 指令优先级

```text
用户当前明确要求
> 根 AGENTS.md
> 当前 Change 的 change.yaml / context.md
> canonical 领域资产与 Accepted Decision
> 项目适配 Skill
> 外部 Skill
> reference/ 中的参考材料
```

## 权威级别

- `authority: canonical`：正式基线，必须遵守；
- `authority: provisional`：仅供评审中的 Change 使用；
- `authority: reference`：只能作为输入，不能覆盖正式基线；
- `authority: generated`：自动生成，不得手工修改。

`lifecycle: draft` 不得同时声明 `authority: canonical`。

## 全局红线

- 不复制旧系统业务代码、表结构或兼容层。
- 不混淆自然人身份、姓名、家庭角色和谱系归属。
- 不混淆血缘、家庭、法律、抚养、谱籍和祭祀承继关系。
- 不以谱书展示结果反推正式业务事实。
- 不绕过审核直接写入正式族谱事实。
- 不把研究材料、示例、生成资产或未批准 Change 当成正式需求。
- 不引入无法建立约束的万能关系或弱多态核心关联。
- 不降低、删除或绕过 Eval、测试和验收标准来完成任务。
- 不在仓库提交真实族人的敏感个人信息。
- 不手工修改 `knowledge/generated/` 或其他 generated 资产。

## Change 要求

非平凡变更必须有独立 Change，并至少包含：

- `change.yaml`：唯一生命周期、Gate 和外部关联状态；
- `context.md`：目标、非目标、影响范围和修改边界；
- `proposal.md`；
- `specs/`；
- `design.md`；
- `tasks.md`；
- `implementation/`；
- `validation/`；
- `reviews/`；
- `evidence/`。

GitHub Issue 是执行视图，批准后的 Change Spec 才是需求事实源。

## 需求开发纪律

- 重要歧义先运行 `grill-with-docs`。
- 新术语和领域边界通过 `domain-modeling` 固化。
- 非平凡需求通过 `to-spec` 形成 OpenSpec Change。
- `to-tickets` 必须拆为可独立验证的纵向切片。
- 编码在预先批准的测试 Seam 上执行 TDD。
- 实现后执行 Standards 与 Spec 双轴评审。
- 合入前运行 `python tools/validate_repo.py`。

## 完成定义

AI 必须证明：目标和非目标满足、领域不变量未破坏、Spec/Task/代码/测试可追踪、正例反例边界案例通过、隐私与安全检查通过、双轴评审无阻断问题。
