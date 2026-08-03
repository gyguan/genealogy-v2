# Genealogy V2

面向中国式商用族谱系统的 AI 原生资产仓。

当前阶段以产品、领域、决策、变更、Skill、知识与验证资产为主，后续代码同样由 AI 在显式 Spec、任务和验证约束下生成。

## AI 标准入口

1. `AGENTS.md`：全仓不可违反的规则；
2. `ai/repo-map.yaml`：仓库导航与权威来源；
3. `changes/active/<change-id>/context.yaml`：当前任务边界；
4. 受影响领域的模型、规则与 Eval；
5. `decisions/` 中已接受的长期决策。

## 需求开发流程

```text
grill-with-docs
→ domain-modeling
→ to-spec
→ OpenSpec 评审
→ to-tickets
→ implement + tdd
→ code-review
→ 证据归档
```

项目适配后的工程 Skill 位于 `skills/engineering/`，安装和调用方式见 `skills/INSTALL.md`。

## 资产流转

```text
product/ + domains/
        ↓
changes/active/<change-id>/
        ↓
skills/ 执行与校验
        ↓
evals/ 验证
        ↓
合入正式基线并归档 Change
```

## 当前目录

```text
ai/          AI 导航、上下文、路由与策略
skills/      AI 可复用执行能力及上游来源记录
product/     产品目标、定位、能力与路线
domains/     领域语义、边界与不变量
knowledge/   当前工程事实和自动提取知识
changes/     单次变更的 OpenSpec 工件和证据
decisions/   已接受的长期产品、领域和架构决策
evals/       领域、跨域和端到端验证资产
reference/   非权威研究、模板和参考材料
```
