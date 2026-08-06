# Proposal

## 背景与问题

仓库已经覆盖 Change、Proposal、Spec、Design Contract、Task/Test 追踪和当前 Head Review，但注册测试尚未实际执行，PR 对 Domain、Decision、Capability 的范围只做粗粒度分类，模板占位 ID 可能进入评审态，high-risk Change 也尚未强制独立人类批准。继续扩展完整审批历史和细粒度 Task 文件映射会显著增加维护成本。

## 目标用户与角色

主要用户是使用 AI 或人工提交 Change 的贡献者、负责业务语义与风险把关的 Reviewer，以及维护 GitHub Actions 和仓库治理规则的 Repository Owner。

## 当前流程与痛点

当前 `tools/check.py` 验证 Test Registry 的结构与追踪，但不会执行当前 PR 所声明 Change 的注册命令；PR 范围校验能判断 Change 类型，却不能阻止修改未声明的具体 Domain、Decision 或 Capability；生成器占位 ID 依赖人工替换；high-risk 与普通 Change 使用同一 Codex Review 规则。

## 目标业务流程

Contributor 声明 Change 并提交 PR → Repository Validation 运行仓库检查 → 精确校验受影响资产 → 在隔离环境执行当前 Change 注册测试 → Codex Review 当前 Head → high-risk 额外获得非作者人类 APPROVED → Release Approval 绑定最终 Head、CI、Review 和测试结果 → 同一个 PR 更新 completed 并合入。

## 关联产品能力

本 Change 只强化仓库研发治理，不新增或修改产品 Capability。

## 目标

以四项低成本门禁补齐执行真实性和高风险把关：运行注册测试、精确校验 affected 范围、禁止评审态占位 ID、high-risk 强制人类批准；同时明确 Release Evidence 不依赖尚未产生的 Merge SHA。

## 非目标

不新增完整 Issue Contract、状态迁移历史、Gate Evidence 在线核验、Changed File 到 Task/Module/Spec 的全链路映射，也不建立 Warning 豁免系统和 post-merge Finalizer。

## 范围与影响领域

修改 `tools/run_change_tests.py`、`tools/validate_pr_change_strict.py`、`tools/validate_change_quality_strict.py`、`tools/validate_design_machine.py`、`tools/validate_pr.py`、GitHub Actions 与治理文档；不修改族谱业务领域、数据模型或产品能力。

## 核心业务约束

普通 Change 不增加额外人工审批；只执行 PR Body 明确声明 Change 的注册测试；测试子进程不得继承 GitHub Token；精确范围只覆盖正式 Domain、Decision、Capability，不强制普通代码文件映射 Task；模板占位符在 Draft 可存在，进入 Review 后必须清零。

## 需求事实来源

- 产品能力：不适用，本 Change 不修改产品能力。
- 领域不变量：不适用，本 Change 不修改族谱领域不变量。
- Accepted Decision：遵守 DEC-0001 的模块与目录边界。
- Issue / 用户确认：Issue #18 及用户明确要求按最小必要方案修改。

## 依赖与前置条件

依赖现有 Test Registry、Change Profile、PR Body Change ID、GitHub Pull Request API、当前 Head Review 与 Required Checks。

## 假设

GitHub Actions 运行环境已提供 Python、Node、Maven 或 Gradle 等常用 Runner；本阶段只允许受控 Runner，不支持任意 shell 脚本。

## 待澄清问题

无待澄清问题。

## 关联 Decision

不修改 Decision；所有新增工具继续位于 `tools/`，配置和 Workflow 继续位于 `.github/`。

## 风险

执行 PR 内注册命令可能增加 CI 时间或暴露凭证；通过仅执行当前 Change、命令白名单、超时和最小环境隔离控制。精确 Capability Diff 需要读取 Base 内容，API 失败时采用失败关闭策略。

## 成功标准

四项规则都有正反例回归；当前 PR 注册测试真实执行；未声明的 Domain、Decision、Capability 修改被阻断；Draft 占位 ID 可生成而 Review-ready 被阻断；standard/lightweight 不增加人类审批，high-risk 必须有当前 Head 人类 APPROVED；完整 CI 和 PR Governance 通过。

## 验收边界

仅以客观可重复规则阻断。测试充分性、业务语义、方案取舍和风险接受仍由独立 Review 判断，不由 Python 自动裁决。
