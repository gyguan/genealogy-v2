# Product Spec Delta

## SPEC-PRODUCT-005 ADDED 可分片的产品能力基线

产品能力必须按能力组拆分存储，并通过统一Manifest发现。Agent应先读取版本和Manifest，再只读取当前Change涉及的能力文件。

### 验收场景

- Manifest列出的每个能力文件存在且只包含一个能力组；
- 未被Manifest列出的能力YAML必须被校验器拒绝；
- Capability ID在全部能力文件中全局唯一；
- 产品Change仍可通过稳定Capability ID追踪，不依赖文件位置。

## SPEC-PRODUCT-006 ADDED 能力类型与责任语义

每项能力必须区分业务、应用或平台类型，并记录主责任领域与协作领域。平台能力必须记录平台治理范围。

### 验收场景

- `primary_domain`和`supporting_domains`只能引用正式领域；
- 主责任领域不得重复出现在协作领域；
- `primary_domain`不得被解释为代码模块归属或直接数据访问授权；
- 后续业务Change必须同时列出受影响Capability和领域。

## SPEC-PRODUCT-007 MODIFIED 版本内承诺与规划置信度

产品能力必须使用`release_priority: must|should|could`表达目标版本内承诺，并使用`planning_confidence: high|medium|low`表达规划确定性。

### 验收场景

- V2.0能力使用candidate状态和low置信度；
- 中远期候选能力不得被解释为正式交付承诺；
- 能力不得依赖目标版本更晚的能力；
- Release和Capability版本引用必须由校验器验证。

## SPEC-PRODUCT-008 ADDED 受治理的纵向版本闭环

V0.x每个版本必须同时覆盖与其范围匹配的录入、来源或审核、授权、查询验证、迁出和恢复能力。

### 验收场景

- V0.1包含基础来源审核和结构化导出；
- V0.2包含账号、基础角色范围、审核记录和备份恢复；
- V0.3复杂谱系与历史语义可查询且可迁出；
- V0.4形成完整证据链与质量治理；
- V0.5形成基础隐私控制、不可变出版快照和可复现交付包；
- V1.0只进行商用级加固与真实项目验收。

## SPEC-PRODUCT-009 MODIFIED Roadmap语义完整性

V0.1—V0.5 Roadmap必须包含用户目标、纵向闭环、主要能力、明确不包含、版本验收、成功指标和核心风险。

### 验收场景

- 任一近期版本缺少规定章节时自动校验失败；
- Roadmap不重复维护全部Capability明细；
- Capability目标版本与Roadmap描述不得冲突；
- V1.1以后明确标记为候选方向并避免实现细节。
