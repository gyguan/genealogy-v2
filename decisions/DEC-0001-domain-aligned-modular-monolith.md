---
id: DEC-0001
title: 领域对齐的模块化单体代码布局
status: accepted
type: architecture
affected_domains:
  - person-registry
  - family-and-kinship
  - lineage-organization
  - source-and-evidence
  - genealogy-project
  - publication
introduced_by: CHG-0001
supersedes: []
superseded_by: null
effective_at: 2026-08-04
---

# 领域对齐的模块化单体代码布局

## 背景

Genealogy V2 当前处于产品、领域和 Change 基线阶段，尚无业务代码。过早按微服务或技术层创建空目录会放大维护成本，也会削弱领域边界。首批代码仍需要明确稳定落位规则，避免 AI 随机创建 `controller/service/repository/common` 等横向目录。

## 决策

首期采用领域对齐的模块化单体。只有产生真实实现时才逐步创建以下目录：

```text
apps/        可部署入口，例如 api、web、worker
modules/     与 domains 中 ID 一一对应的业务模块
platform/    身份、持久化、审计、隐私、文件等无业务语义的技术能力
contracts/   对外 API、领域事件和导入导出稳定契约
tests/       架构、契约、集成与端到端测试
```

每个 `modules/<domain-id>/` 内部按领域、应用、端口、适配器和测试组织，不在仓库根部建立跨领域的 `controllers/`、`services/`、`repositories/`。

模块依赖必须遵循 `domains/context-map.yaml`。`platform/` 不得拥有族谱业务规则；`common/`、`shared/`、`utils/`、`base/` 等泛化目录默认禁止，确有稳定共享内核时必须另建 Decision。

## 原因

- 保持文档领域与代码模块一一映射，降低 AI 的上下文定位成本；
- 在单一部署单元内保留清晰边界，避免过早承担分布式复杂度；
- 允许未来基于真实容量、团队和发布证据拆分部署单元，而不改变领域模型；
- 便于通过架构测试自动检查依赖方向。

## 备选方案

- 按技术层组织：跨领域修改范围过大，AI 容易混淆业务边界，不采用。
- 首期微服务：当前缺少独立扩缩容、团队自治和发布节奏证据，不采用。
- 无约束单体：短期简单但会快速形成循环依赖，不采用。

## 影响

- 当前不创建空代码目录；第一个实现 Change 按本 Decision 创建最小必要目录。
- 后续校验器应在出现业务代码后增加模块名、依赖方向和架构测试校验。
- 拆分微服务必须由新的 Decision 基于运行数据和组织边界提出。

## 迁移与回退

当前无业务代码，无迁移成本。若模块化单体不满足要求，可在保持领域契约和模块边界的前提下逐模块拆分部署。

## 关联 Change

- `CHG-0001-close-directory-review-findings`
