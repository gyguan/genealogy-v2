---
id: DEC-0004
title: evidence-before-formal-fact
status: accepted
type: product
affected_domains:
  - person-registry
  - family-and-kinship
  - lineage-organization
  - source-and-evidence
introduced_by: CHG-0002
supersedes: []
superseded_by: null
effective_at: 2026-08-04
---

# 证据先于正式事实

## 背景

族谱资料可能来自旧谱、口述、碑刻、档案和个人填报，不同来源之间经常存在冲突。如果直接覆盖人物和关系字段，将无法解释结论来源和修订过程。

## 决策

Genealogy V2 将来源、引文、主张、证据、审核结论和正式事实分层管理。关键人物、关系、日期、地点和谱系归属必须经过授权审核后才能成为正式事实。

## 原因

- 修谱结论需要能够追溯和复核；
- 冲突资料应并存，不应通过覆盖历史数据消失；
- 人物合并、关系更正和谱书勘误都依赖完整证据链；
- AI抽取结果只能作为候选主张，不能直接成为正式事实。

## 备选方案

1. 直接修改正式人物和关系记录，只保留操作日志；
2. 对冲突内容使用备注字段；
3. 仅在出版阶段补充来源脚注。

这些方案无法表达主张之间的支持、反驳和不确定关系。

## 影响

V0.4建设完整证据与质量治理。在此之前，V0.1—V0.3的关键事实也必须预留来源和审核边界，不得设计为任何人可直接覆盖。

## 迁移与回退

早期版本可以使用简化来源引用，但正式数据模型必须允许后续迁移为完整的来源—主张—证据链。

## 关联 Change

- `changes/CHG-0002-product-blueprint-and-roadmap/`
