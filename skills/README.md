# Skills

Skill 分为三类：

- `workflows/`：用户主动调用的端到端编排；
- `disciplines/`：Agent 可自动调用的工程纪律；
- `validators/`：确定性或半确定性校验与门禁。

`catalog.yaml` 是 Skill 分类、调用方式和路径的唯一机器索引。`upstream/` 只记录来源与许可，不参与自动执行。
