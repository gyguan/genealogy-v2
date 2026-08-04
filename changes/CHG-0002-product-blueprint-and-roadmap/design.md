# Design

## 方案概览

采用“产品正式基线 + Change规划过程 + Decision长期取舍”的三层结构：

- `product/README.md` 保存产品定位、客户、价值、原则和边界；
- `product/capability-map.yaml` 保存全量能力及目标版本；
- `product/roadmap.md` 保存版本用户闭环、边界和验收；
- `changes/CHG-0002-product-blueprint-and-roadmap/` 保存本次规划增量、任务和证据；
- `decisions/DEC-0002` 至 `DEC-0005` 保存长期产品取舍。

能力地图覆盖完整长期方向，但Roadmap只对近期版本细化，避免把未来假设固化为详细需求。

## 领域与数据影响

本Change不修改领域职责和依赖。产品能力按照当前六个领域指定主要责任域：

- 人物身份和历史人物信息归属 `person-registry`；
- 家庭与复杂亲属关系归属 `family-and-kinship`；
- 支房、字辈、世次和迁徙组织归属 `lineage-organization`；
- 来源、主张、证据和数字资产归属 `source-and-evidence`；
- 项目、组织、采集、审核和平台治理归属 `genealogy-project`；
- 查询阅读、编修和出版归属 `publication`。

真实业务Change可以提出能力责任域调整，但必须同步评审领域边界。

## 接口与模块边界

本Change不定义软件接口和代码模块。Capability ID作为产品到Spec的追踪入口，后续业务Change再将Capability映射到领域Spec、模块、接口和测试。

## 安全与隐私

产品路线将角色权限、数据范围、在世人物隐私、来源权利、操作审计和出版脱敏纳入V1.0商用门槛。任何AI能力只能生成候选、提示和建议，不得自动确认正式人物或关系事实。

## 测试 Seam

公共验证Seam包括：

1. `python tools/validate_repo.py` 校验Capability、Decision、Change、Spec、Task和Evidence引用；
2. `python -m unittest discover -s tools/tests -p 'test_*.py'` 验证仓库规则回归；
3. 人工产品评审检查能力覆盖、版本闭环、非目标和长期决策一致性。

## 失败、补偿与回滚

若能力地图过细或版本排序不符合真实项目，应通过新的产品Change调整Capability字段和Roadmap，不删除历史Change和Decision。若长期决策需要改变，必须新增Decision并建立supersedes关系。

## 迁移方案

将原有六项粗粒度P0能力扩展为全量能力地图，保留已有稳定ID并补充描述、目标版本、状态和依赖。原P0/P1/P2含义调整为版本关键、重要增强和后续候选，但不改变字段名以兼容当前校验器。

## 备选方案与权衡

1. **先开发V0.1再补产品规划**：能够更快编码，但容易在真实需求中反复讨论产品边界；
2. **一次性编写全部详细PRD**：覆盖完整，但会产生大量未经验证的实现假设；
3. **仅维护Roadmap，不维护Capability Map**：简洁但无法提供稳定追踪ID和依赖关系。

最终选择全量能力级规划、近期版本级细化和当前Change级详细设计的分层方案。
