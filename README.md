# Genealogy V2

面向中国式商用族谱系统的 AI 辅助研发项目。

## AI 开发入口

1. 阅读 `AGENTS.md`；
2. 阅读当前 `changes/<change-id>/change.yaml` 与 `proposal.md`；
3. 阅读受影响的 `domains/` 领域资产和相关 `decisions/`；
4. 按 `skills/` 中的需求开发流程执行；
5. 合入前运行 `python tools/validate_repo.py`。

## 需求开发流程

```text
grill-with-docs
→ domain-modeling
→ to-spec
→ OpenSpec 评审
→ to-tickets
→ implement + tdd
→ code-review
→ repository validation
```

## 核心目录

```text
product/     产品定位、能力清单和路线
domains/     领域术语、边界与不变量
changes/     单次需求的 OpenSpec、设计、任务和证据
decisions/   需要长期保留的关键决策
skills/      AI 需求开发 Skill
tools/       Change 创建和仓库校验工具
.github/     PR 模板与自动校验
```

仅在产生真实需求时增加资产，不为未来可能性预建空目录。
