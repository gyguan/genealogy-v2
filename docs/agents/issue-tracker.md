# Issue Tracker

本仓库使用 GitHub Issues：`gyguan/genealogy-v2`。

## 定位

- GitHub Issue 是需求、任务和缺陷的协作与执行视图。
- `changes/active/<change-id>/` 中批准的 OpenSpec 工件是需求事实源。
- Issue 不应复制完整 Spec；应引用 Change ID、目标、验收标准和阻塞关系。

## 任务拆分

`to-tickets` 按依赖顺序创建纵向切片，每个 Ticket 必须：

- 在单个新上下文窗口内可完成；
- 独立可演示或验证；
- 声明阻塞 Ticket；
- 引用 Change ID 和对应 Spec 条目；
- 不包含容易过期的具体文件路径。
