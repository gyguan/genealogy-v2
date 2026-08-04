# Tasks

## TASK-PRODUCT-006 重构产品规划资产
- Specs: SPEC-PRODUCT-005, SPEC-PRODUCT-006
- Status: completed
- Dependencies: none
- Scope: 拆分Release、Manifest和15个能力组文件，升级Capability字段
- Acceptance: AI可按版本和能力组定向读取，稳定ID不依赖文件位置
- Tests: Manifest、文件清单、字段和ID校验
- Evidence: evidence/TASK-PRODUCT-006.md
- Rollback: 回滚CHG-0003并恢复CHG-0002产品基线

## TASK-PRODUCT-007 补齐产品能力缺口
- Specs: SPEC-PRODUCT-006, SPEC-PRODUCT-008
- Status: completed
- Dependencies: TASK-PRODUCT-006
- Scope: 新增家庭单元、账号访问、隐私生命周期、分阶段迁出、机构运营和生态候选能力
- Acceptance: 能力链覆盖基础家庭、协作身份、授权、迁出和候选生态
- Tests: Capability ID、依赖、领域和版本引用校验
- Evidence: evidence/TASK-PRODUCT-007.md
- Rollback: 删除新增能力并恢复原依赖

## TASK-PRODUCT-008 调整版本纵向闭环
- Specs: SPEC-PRODUCT-007, SPEC-PRODUCT-008, SPEC-PRODUCT-009
- Status: completed
- Dependencies: TASK-PRODUCT-007
- Scope: 前移基础来源审核、权限、备份、迁出和出版脱敏，收敛V1.0
- Acceptance: V0.1—V0.5均形成可验收纵向闭环，V1.0只做商用加固
- Tests: 版本倒挂检测和Roadmap章节检测
- Evidence: evidence/TASK-PRODUCT-008.md
- Rollback: 恢复原目标版本并重新评审DEC-0006

## TASK-PRODUCT-009 建立长期产品Decision
- Specs: SPEC-PRODUCT-006, SPEC-PRODUCT-008
- Status: completed
- Dependencies: TASK-PRODUCT-008
- Scope: 新增DEC-0006和DEC-0007
- Acceptance: 纵向版本原则和Capability责任语义成为Accepted Decision
- Tests: Decision元数据、Change引用和必备章节校验
- Evidence: evidence/TASK-PRODUCT-009.md
- Rollback: 将Decision标记为superseded并提供替代Decision

## TASK-PRODUCT-010 增强自动校验与回归测试
- Specs: SPEC-PRODUCT-005, SPEC-PRODUCT-006, SPEC-PRODUCT-007, SPEC-PRODUCT-009
- Status: completed
- Dependencies: TASK-PRODUCT-006, TASK-PRODUCT-008
- Scope: 支持分片能力、版本顺序、循环、版本倒挂、字段和Roadmap完整性校验
- Acceptance: 正向仓库通过，构造反例被准确阻断
- Tests: python tools/validate_repo.py；python -m unittest discover -s tools/tests -p 'test_*.py'
- Evidence: evidence/TASK-PRODUCT-010.md
- Rollback: 回滚校验器和测试修改
