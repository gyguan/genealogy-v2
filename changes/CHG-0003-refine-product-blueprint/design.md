# Design

## 方案概览

产品资产采用四层结构：

1. `product/README.md`：产品定位、原则和边界；
2. `product/releases.yaml`：版本机器事实；
3. `product/capability-map.yaml`：能力文件Manifest和全局规则；
4. `product/capabilities/*.yaml`：按能力组拆分的正式能力；
5. `product/roadmap.md`：面向人类的用户闭环、验收、指标和风险。

本 Change 新增 `DEC-0006` 与 `DEC-0007`，分别约束纵向版本切分和Capability责任语义。

## 领域与数据影响

Capability由单一 `domain` 升级为 `primary_domain` 与 `supporting_domains`，同时增加 `capability_type`。这些字段表达产品责任，不改变领域Context Map。新增家庭单元能力，补齐账号访问、隐私、迁出和生态候选能力。

## 接口与模块边界

本 Change 不定义软件接口或模块。`primary_domain` 不得被工具直接转换为模块依赖；后续业务 Change 必须结合领域资产和 Architecture Decision 决定代码落位。

## 安全与隐私

基础账号、项目角色、支房数据范围和在世人物隐私前移到 V0.2；V1.0再完成细粒度用途授权、审批权分离、隐私请求和安全审计。AI与跨谱能力保持candidate，并明确禁止自动合并和绕过审核。

## 测试 Seam

- YAML可解析；
- Manifest列出的能力文件完整且不存在未列入文件；
- Release和Capability ID唯一；
- 字段枚举、领域引用、版本引用和依赖合法；
- 能力依赖无循环且不依赖更晚版本；
- V0.1—V0.5 Roadmap具备规定章节；
- Change、Decision、Spec、Task和Evidence引用保持有效；
- 正向仓库与构造反例均由自动化测试验证。

## 失败、补偿与回滚

若拆分后的加载逻辑影响现有工具，可回滚本 Change，原产品资产历史仍保留在 `CHG-0002`。不得通过恢复超大单文件绕过字段和版本一致性规则；需要修改结构时应建立新的产品 Change。

## 迁移方案

- 将旧 `capability-map.yaml` 的12个能力组迁移到独立文件；
- `capability-map.yaml`改为Manifest；
- Release定义迁移至 `releases.yaml`；
- 原 `priority`改为目标版本内的 `release_priority`；
- 原 `domain`改为`primary_domain`并补充`supporting_domains`；
- V2.0及部分中远期能力改为candidate和低置信度；
- 更新README、Roadmap、校验器和回归测试。

## 备选方案与权衡

1. 继续维护单文件：最简单，但AI上下文和协作冲突会持续恶化；
2. 只补字段不调整版本：无法解决治理能力过晚和V1.0过重；
3. 将全部能力改写为详细PRD：会过早固化实现；
4. 只修改Roadmap：不能保证机器可追踪和依赖一致。

最终选择“稳定Capability级规划、近期纵向闭环、当前Change详细设计”的分层方式。
