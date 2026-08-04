---
id: DEC-0003
title: complex-chinese-kinship-is-core
status: accepted
type: product
affected_domains:
  - person-registry
  - family-and-kinship
  - lineage-organization
introduced_by: CHG-0002
supersedes: []
superseded_by: null
effective_at: 2026-08-04
---

# 复杂中国式谱系是核心差异化

## 背景

通用家谱产品通常以配偶和父母子女关系为中心，难以正确表达继嗣、出嗣、兼祧、入赘、字辈、支房和谱籍承继等中国式谱系语义。

## 决策

Genealogy V2 将复杂中国式谱系作为核心产品能力。血缘、婚姻、法律、抚养、家庭、谱籍和祭祀承继关系必须保持独立语义，不使用单一万能关系模型替代。

## 原因

- 复杂谱系是中国式专业族谱区别于通用家谱的关键；
- 关系维度混淆会造成世次、归属、出版和历史解释错误；
- 后期从简单模型迁移到多维关系模型成本极高；
- 专业修谱机构需要可解释、可审核和可更正的关系表达。

## 备选方案

1. 使用一个关系表和可扩展关系类型枚举；
2. 只实现普通配偶和亲子，复杂关系以备注保存；
3. 由出版模板临时修正展示。

这些方案无法形成可靠约束，也会把展示结果误当作业务事实。

## 影响

V0.1先验证人物、普通家庭关系和谱系组织边界；V0.3集中交付复杂谱系能力。所有后续查询、证据和出版能力必须基于多维关系语义。

## 迁移与回退

若某类关系尚未实现，应保留为明确的未支持能力，不得退化为备注或无约束自定义关系。

## 关联 Change

- `changes/CHG-0002-product-blueprint-and-roadmap/`
