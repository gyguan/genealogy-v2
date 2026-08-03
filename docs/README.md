# Genealogy V2 文档导航

本目录只保留能够长期指导产品、架构和实现的权威文档。

## 阅读顺序

开始任何非平凡任务前，按以下顺序阅读：

```text
根 README.md
  → 根 AGENTS.md
  → 当前任务对应的权威文档
  → 已批准的 Issue / ADR / API 契约
```

不要求无差别加载全部文档，应读取与任务相关的最小充分集合。

## 权威文档

| 目录 | 文档 | 用途 |
|---|---|---|
| 产品 | [产品定义](product/product-definition.md) | 明确用户、场景、范围、非目标和成功标准 |
| 产品 | [领域模型](product/domain-model.md) | 定义核心对象、事实、命令和业务不变量 |
| 架构 | [系统架构](architecture/system-architecture.md) | 定义架构形态、模块边界、依赖方向和运行约束 |
| 架构 | [架构决策清单](architecture/decision-backlog.md) | 收敛进入编码前必须完成的关键 ADR |
| 前端 | [设计系统](frontend/design-system.md) | 定义信息架构、页面模式、视觉语言和交互规则 |
| 规范 | [API 设计](standards/api-design.md) | 定义读写契约、错误、并发、分页和版本规则 |
| 规范 | [数据库设计](standards/database-design.md) | 定义事实建模、约束、时间、迁移和性能规则 |
| 规范 | [权限与隐私](standards/authorization-and-privacy.md) | 定义角色、范围、隐私、导出和审计规则 |
| 治理 | [文档驱动开发](governance/document-driven-development.md) | 定义从需求到交付的评审和验收流程 |
| 路线 | [实施路线](roadmap/implementation-roadmap.md) | 定义阶段顺序、依赖关系和阶段门禁 |

## 文档状态

权威文档应在标题下标明状态：

- `Draft`：正在形成，不得作为实现承诺；
- `Review`：内容基本完整，等待评审；
- `Approved`：可作为 Issue 和实现依据；
- `Superseded`：已被新的权威文档或 ADR 替代；
- `Archived`：仅用于历史追溯。

## 文档新增原则

只有满足以下条件才新增文档：

1. 存在明确且长期稳定的主题；
2. 无法合理纳入现有权威文档；
3. 有明确读者和使用场景；
4. 能影响设计决策、实现边界或验收；
5. 不与现有文档重复定义规则。

会议纪要、临时讨论、探索笔记和未验证方案不得进入权威目录。

## 变更要求

- 领域不变量变化必须同步产品、架构和验收说明。
- API 或数据库策略变化必须说明兼容、迁移或补偿方式。
- 权限和隐私变化必须说明默认拒绝规则及审计影响。
- 页面模式变化必须说明对现有信息架构和可访问性的影响。
- 文档被替代时必须建立明确引用，不静默删除决策背景。
