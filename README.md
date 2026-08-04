# Genealogy V2

面向中国式商用族谱系统的 AI 辅助研发项目。

## AI 开发入口

1. 阅读 `AGENTS.md` 与 `SECURITY.md`；
2. 阅读当前 `changes/<change-id>/change.yaml` 与 `proposal.md`；
3. 读取 `product/releases.yaml`、`product/capability-map.yaml`，并只加载本次涉及的 `product/capabilities/*.yaml`；
4. 阅读 `domains/context-map.yaml`、受影响领域文件和相关 `decisions/`；
5. 按 `skills/` 中的需求开发流程执行；
6. 合入前运行 `python tools/validate_repo.py` 和仓库回归测试。

## 需求开发流程

```text
grill-with-docs
→ domain-modeling
→ to-spec
→ openspec-validation
→ OpenSpec 评审
→ to-tickets
→ implement + tdd
→ code-review
→ repository validation
```

## 核心目录

```text
product/     产品定位、版本、分组能力和路线
domains/     领域术语、边界、不变量与依赖图
changes/     单次需求的 OpenSpec、设计、任务和证据
decisions/   需要长期保留的关键决策
skills/      AI 需求开发 Skill
tools/       Change 创建和仓库校验工具
.github/     PR 模板与自动校验
```

仅在产生真实需求时增加资产，不为未来可能性预建空目录。新增顶层资产类型必须通过独立 Change 和 Accepted Decision，并同步更新本文件与仓库校验器。
