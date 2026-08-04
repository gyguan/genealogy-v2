# Proposal

## 背景与问题

现有 `design.md` 只有八个宽泛标题，能够提示方案方向，但不能保证 AI 明确设计范围、逐项判断适用性、遵守领域与架构约束、建立 Spec/Test 追踪，或在进入实现前关闭开放问题。

## 关联产品能力

本 Change 属于仓库治理，不新增或修改产品 Capability；它为后续产品、领域与工程 Change 提供统一设计契约。

## 目标

将 `design.md` 升级为机器可读设计契约；强制正式资产引用、适用性、稳定设计 ID、Spec/Test 追踪和开放问题闭环；接入统一检查和 GitHub Actions。

## 非目标

不新增 PRD/HLD/LLD 平行目录，不要求所有需求都设计状态机、API、事件、页面或迁移，不修改产品能力、领域不变量或业务代码，不以自动校验替代人工语义评审。

## 范围与影响领域

更新 Change 模板、AI 规则、to-spec、openspec-validation、新 Change 生成器、统一检查入口、设计校验器和回归测试；不修改任何族谱领域事实。

## 关联 Decision

遵守 DEC-0001；设计中的模块落位必须维持领域对齐的模块化单体边界。

## 风险

校验过严可能误阻断轻量设计，稳定 ID 会增加少量写作成本，结构通过也不能证明业务语义正确；通过 applicability、契约版本和人工双轴评审降低风险。

## 成功标准

从 CHG-0007 起，新 Change 自动声明 `design_contract_version: 1` 并初始化 Design Frontmatter；required 与 not-applicable 可确定性校验；Spec、规则、测试和开放问题可追踪；CHG-0001 至 CHG-0006 保持兼容；`python tools/check.py` 全部通过。
