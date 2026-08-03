# 架构文档

本目录只维护跨模块、长期稳定且会影响实现边界的架构设计。

## 当前文档

- [系统架构](system-architecture.md)：总体形态、模块边界、依赖方向、读写架构和演进条件。
- [首批架构决策清单](decision-backlog.md)：进入编码前必须形成 ADR 的关键决策。

## 新增 ADR 的条件

只有满足以下条件才建立 ADR：

- 决策会影响多个模块或公共契约；
- 存在两个以上合理候选方案；
- 选择会产生长期成本或迁移后果；
- 未来需要理解当时为什么这样选择。

局部类设计、普通查询 SQL、页面排版和短期任务安排不建立 ADR。

ADR 文件建议命名：

```text
adr-001-<decision-name>.md
```

状态使用：`Proposed`、`Accepted`、`Superseded`、`Rejected`。
