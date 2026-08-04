# Tasks

## TASK-PRODUCT-001 梳理全量产品能力

- Specs: SPEC-PRODUCT-001
- Status: completed
- Depends on: none
- Tests: TEST-PRODUCT-COVERAGE-001
- Evidence: evidence/TASK-PRODUCT-001.md

### 纵向范围

从目标客户和真实修谱流程出发，梳理组织、项目、人物、谱系、亲属、历史、证据、采集、数字化、查询、出版和平台治理能力。

### 验收标准

能力覆盖从项目创建到数据与谱书交付的完整链路，且每项能力具有稳定ID和明确价值。

### 完成定义

能力组和能力清单写入 `product/capability-map.yaml`，未混入页面、API和数据库设计。

### 回滚条件

若能力组无法映射当前产品定位或领域责任，应回退并重新评审产品范围。

## TASK-PRODUCT-002 分配目标版本、优先级和依赖

- Specs: SPEC-PRODUCT-001, SPEC-PRODUCT-002, SPEC-PRODUCT-003
- Status: completed
- Depends on: TASK-PRODUCT-001
- Tests: TEST-PRODUCT-TRACEABILITY-001
- Evidence: evidence/TASK-PRODUCT-002.md

### 纵向范围

为全部能力分配所属领域、目标版本、P0/P1/P2优先级、状态和前置能力。

### 验收标准

V0.1—V1.2的核心能力能够形成连续依赖链，V2.0候选能力具有明确治理前提。

### 完成定义

能力字段完整，版本定义和优先级规则写入能力地图。

### 回滚条件

若能力依赖产生循环或版本无法形成用户闭环，重新调整能力粒度和版本归属。

## TASK-PRODUCT-003 建立版本路线与验收边界

- Specs: SPEC-PRODUCT-002, SPEC-PRODUCT-003
- Status: completed
- Depends on: TASK-PRODUCT-002
- Tests: TEST-ROADMAP-CLOSURE-001
- Evidence: evidence/TASK-PRODUCT-003.md

### 纵向范围

定义V0.1、V0.2、V0.3、V0.4、V0.5、V1.0、V1.1、V1.2和V2.0的用户目标、主要能力、非目标和验收标准。

### 验收标准

近期版本形成清晰用户闭环，V1.0以一部真实族谱端到端交付为商用验收。

### 完成定义

路线写入 `product/roadmap.md`，并明确不同时间范围的规划深度。

### 回滚条件

若版本只是功能堆积而无可观察用户结果，重新按端到端闭环拆分。

## TASK-PRODUCT-004 固化长期产品决策

- Specs: SPEC-PRODUCT-004
- Status: completed
- Depends on: TASK-PRODUCT-003
- Tests: TEST-DECISION-LINK-001
- Evidence: evidence/TASK-PRODUCT-004.md

### 纵向范围

将专业修谱优先、复杂中国式谱系、证据先于正式事实和数据可迁移固化为长期Decision。

### 验收标准

每项Decision为accepted状态、关联CHG-0002并说明背景、原因、备选方案、影响和回退方式。

### 完成定义

新增DEC-0002至DEC-0005，并在产品定位和路线中体现约束。

### 回滚条件

若某项取舍仅影响单一版本且易于逆转，应移回Roadmap而非长期Decision。

## TASK-PRODUCT-005 校验并形成产品基线

- Specs: SPEC-PRODUCT-001, SPEC-PRODUCT-002, SPEC-PRODUCT-003, SPEC-PRODUCT-004
- Status: completed
- Depends on: TASK-PRODUCT-001, TASK-PRODUCT-002, TASK-PRODUCT-003, TASK-PRODUCT-004
- Tests: TEST-REPOSITORY-VALIDATION-001, TEST-PRODUCT-REVIEW-001
- Evidence: evidence/TASK-PRODUCT-005.md

### 纵向范围

检查产品定位、能力地图、Roadmap、Decision、Change、Spec、Task和Evidence之间的一致性。

### 验收标准

仓库校验与回归测试通过，产品评审无阻断问题，正式产品基线可供后续业务Change引用。

### 完成定义

全部Gate批准并保存Evidence，CHG-0002状态为completed。

### 回滚条件

若自动校验失败或存在未解决的产品范围冲突，不得合入正式基线。
