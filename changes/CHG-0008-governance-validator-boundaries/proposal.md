# Proposal

## 背景与问题

PR #11 与 PR #9 合入后，最终 Head 的 Codex Review 分别追加了四个和两个未解决线程。复检确认当前 `main` 仍存在 Decision 类型与历史路径解析、Spec fenced 示例识别，以及 Design CommonMark 段落状态判断等六个确定性缺口。这些缺口会误阻断合法 PR，或让示例内容错误参与正式治理判断。

## 关联产品能力

本 Change 仅修复仓库治理工具，不新增或修改产品 Capability。

## 目标

对齐 Decision canonical 类型与 Change 类型；正确读取 Decision Head/Base 元数据；区分正式 Decision 与支持文档；屏蔽 Spec fenced 示例；修正 lazy block quote 与列表项段落状态；为六项问题建立稳定回归测试。

## 非目标

不使用 Python 判断 Decision 内容质量、架构方案优劣或风险是否可接受；不引入完整 Markdown 解析器；不降低 strict Change、Design Contract 或 PR 范围门禁。

## 范围与影响领域

修改 `tools/validate_pr_change.py`、`tools/validate_pr_change_strict.py`、`tools/validate_change_quality_strict.py`、`tools/validate_design.py` 及对应测试；不修改族谱领域模型、产品范围和业务数据。

## 关联 Decision

不修改现有 Decision。实现必须继续遵守 DEC-0001 的模块边界，并以 `validate_repo.py` 中的 Decision 类型集合为 canonical schema。

## 风险

历史路径读取依赖 GitHub Contents API；Markdown 状态机边界若处理不当可能产生新的误报。通过纯函数拆分、Base 内容注入测试、正反例配对和最终 Head Review 控制风险。

## 成功标准

六项反例均有回归测试；architecture/compliance Decision、rename/delete、`decisions/README.md`、Spec fenced 示例、lazy quote 和列表项段落场景均得到正确结果；`python tools/check.py` 与 PR 在线范围校验通过；最新 Head 不存在未解决 Review Thread。
