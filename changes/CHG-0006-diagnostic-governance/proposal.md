# Proposal
## 背景与问题
仓库已经具备较强的结构、引用、状态和 PR Head 门禁，但内容完整性、端到端追踪和实际 Diff 范围仍主要依赖文字规范。继续把所有质量判断都做成硬门禁，会错误替代业务和技术评审。
## 关联产品能力
本次不改变族谱业务能力，仅增强研发治理能力。
## 目标
建立 Error、Warning、Review-only 三级诊断模型；对新 Change 强制内容完整性、Spec/Task/Test 双向追踪；对 PR 的声明 Change 与实际修改范围进行在线校验。
## 非目标
不判断领域模型是否正确、方案是否最优、产品价值是否成立，也不在本期引入业务代码构建、数据库迁移和部署门禁。
## 范围与影响领域
影响 tools、changes 模板、GitHub Actions、贡献规则和治理文档，不修改业务领域事实。
## 关联 Decision
不新增长期架构 Decision；三级诊断是现有治理原则的可执行化。
## 风险
严格规则可能破坏历史 Change；采用 quality_policy: strict 仅强制新 Change，历史 Change 以 Warning 方式迁移。
## 成功标准
统一检查输出三级摘要；严格 Change 的空文档、无 Scenario、无 Task/Test 覆盖会失败；Warning 和 Review-only 不改变退出码；PR 修改范围超出声明 Change 类型时失败。
