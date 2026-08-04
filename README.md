# Genealogy V2

面向中国式商用族谱系统的 AI 原生工程仓。产品、领域、变更、Skill、验证和后续代码均以可追踪、可校验的资产驱动。

## AI 标准入口

1. `AGENTS.md`：全仓不可违反的规则；
2. `ai/repo-map.yaml`：仓库导航和权威来源；
3. `changes/active/<change-id>/change.yaml`：当前 Change 唯一状态源；
4. `changes/active/<change-id>/context.md`：目标、非目标和任务边界；
5. 受影响领域的 `manifest.yaml`、规则、Decision 和 Eval。

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
→ 证据归档
```

## 一级目录

```text
ai/          AI 导航、路由、上下文包和兼容策略
product/     产品愿景、定位、能力和路线
domains/     领域语义、边界、不变量和领域 Eval
changes/     单次变更的 OpenSpec、实现包、评审和证据
decisions/   长期产品、领域、架构和合规决策
skills/      可安装的工作流、工程纪律和确定性校验器
evals/       跨领域、端到端和发布门禁验证
schemas/     仓库治理资产的机器 Schema
tools/       创建、校验和归档 Change 的确定性工具
knowledge/   当前实现的人工知识和自动生成索引
docs/agents/ 外部 Agent Skill 的兼容阅读层
reference/   非权威研究、模板和参考材料
```

仓库规则必须能被自动校验。文档约束不能只依赖 Agent 自觉遵守。
