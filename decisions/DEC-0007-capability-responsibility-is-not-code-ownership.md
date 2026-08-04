---
id: DEC-0007
title: capability-responsibility-is-not-code-ownership
status: accepted
type: product
affected_domains:
  - person-registry
  - family-and-kinship
  - lineage-organization
  - source-and-evidence
  - genealogy-project
  - publication
introduced_by: CHG-0003
supersedes: []
superseded_by: null
effective_at: 2026-08-04
---

# 产品能力责任不等同于代码归属

## 背景

产品能力经常跨越多个领域和平台能力。例如人物详情需要人物、亲属、谱系和证据数据，权限与迁出能力也服务多个业务领域。若 Capability 只使用一个 `domain` 字段，AI 容易把产品责任领域误解为代码模块归属或直接数据访问权限。

## 决策

产品能力必须区分：

- `capability_type`：业务、应用或平台能力；
- `primary_domain`：对产品语义和结果负责的主领域；
- `supporting_domains`：共同提供语义或事实的协作领域；
- `platform_area`：平台能力的技术治理范围。

这些字段只表达产品责任和协作关系，不授权代码模块依赖、跨域数据库访问或实现落位。代码边界必须由领域 Context Map、Architecture Decision 和当前 Change 的设计共同决定。

## 原因

- 避免将查询、出版和平台能力错误落入单一领域模块；
- 让 AI 能够先选择正确上下文，再由设计决定实现方式；
- 区分产品能力依赖、业务领域依赖和代码模块依赖；
- 支持后续把跨域查询实现为应用服务、契约或快照，而不是直接访问内部表；
- 保持 Capability Map 稳定，不与具体技术架构绑定。

## 备选方案

1. 每项能力只保留一个 `domain` 字段；
2. 直接在 Capability 中填写代码模块和服务；
3. 将所有跨域能力归入 `genealogy-project` 或 `publication`。

这些方案会模糊领域边界，或让产品规划过早绑定实现。

## 影响

- Capability 资产按能力组拆分，并增加类型、主责任领域、协作领域和平台范围；
- 校验器检查领域合法性，但不从 Capability 自动生成代码依赖；
- 业务 Change 必须将 Capability 映射到受影响领域、Spec 和设计；
- 后续 Architecture Test 需要验证代码依赖是 Context Map 允许关系的子集。

## 迁移与回退

原 `domain` 字段迁移为 `primary_domain`，并根据依赖补充 `supporting_domains`。如果未来需要更丰富的责任模型，可增加责任角色，但不得恢复“一个字段同时表达产品责任和代码归属”的含义。

## 关联 Change

- `changes/CHG-0003-refine-product-blueprint/`
