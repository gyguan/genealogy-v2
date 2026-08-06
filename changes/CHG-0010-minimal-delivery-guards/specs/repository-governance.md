# Repository Governance Spec Delta

## ADDED

## SPEC-GOV-MIN-001 当前 PR 的注册测试必须真实执行
#### Requirement
Repository Validation 必须只读取 PR Body 声明的 Change，执行其 `tests.yaml` 注册命令，并使用受控 Runner、单命令超时和不含 GitHub Token 的最小子进程环境。
#### Scenario SCN-GOV-MIN-001-01 合法注册命令执行
- Given: PR 声明一个存在的 Change，且 Test Registry 使用允许的 Python、npm、Maven 或 Gradle Runner
- When: Repository Validation 执行注册测试阶段
- Then: 命令在仓库根目录运行，全部退出码为零时阶段通过
#### Scenario SCN-GOV-MIN-001-02 命令失败或超时
- Given: 任一注册测试返回非零退出码或超过配置超时
- When: Repository Validation 执行注册测试阶段
- Then: 阶段失败并输出 Change ID、Test ID 和失败原因
#### Scenario SCN-GOV-MIN-001-03 凭证与命令安全
- Given: 注册命令包含 shell 操作符、任意可执行路径或尝试读取 GitHub Token
- When: 校验器解析或执行命令
- Then: 危险命令被拒绝，合法测试子进程也不能继承 GitHub Token

## SPEC-GOV-MIN-002 正式资产修改必须精确匹配 Change 影响范围
#### Requirement
PR 修改正式 Domain、Decision 或 Capability 时，实际变化的资产 ID 必须出现在所有声明 Change 对应的 `affected_domains`、`affected_decisions` 或 `capabilities` 并集中。
#### Scenario SCN-GOV-MIN-002-01 Domain 与 Decision 精确范围
- Given: PR 修改 `domains/<id>.md` 或 `decisions/DEC-xxxx-*.md`
- When: 执行 PR Change 范围校验
- Then: 对应 Domain 或 Decision ID 未声明时校验失败
#### Scenario SCN-GOV-MIN-002-02 Capability 记录级差异
- Given: PR 修改一个包含多个 Capability 的分组 YAML
- When: 比较 Base 与 Head 中按 ID 索引的 Capability 记录
- Then: 只要求真实新增、删除或内容变化的 Capability ID 被声明，未变化记录不产生额外负担

## SPEC-GOV-MIN-003 评审态不得保留模板占位 ID
#### Requirement
Draft 可以保留生成器占位 ID；Change 进入 review、approved、implementing 或 completed 后，Spec、Scenario、Task、Test 和机器设计稳定 ID 不得包含模板占位 Token 或 `0000` 占位段。
#### Scenario SCN-GOV-MIN-003-01 Draft 初始化
- Given: `new_change.py` 刚创建 Draft Change 并生成 `SPEC-REPLACE-ME`
- When: 贡献者尚未进入 Review
- Then: 初始化过程保持可用，不因占位 ID 阻断创建
#### Scenario SCN-GOV-MIN-003-02 Review-ready 占位 ID
- Given: Change 已进入 Review 或后续状态，任一正式追踪 ID 包含 REPLACE-ME、EXAMPLE、SAMPLE、TEMPLATE、PLACEHOLDER、XXXX 或 0000 占位段
- When: 执行 strict Change 或 machine Design 校验
- Then: 输出确定性 Error 并阻断

## SPEC-GOV-MIN-004 high-risk Change 必须获得当前 Head 人类批准
#### Requirement
所有 Change 继续要求当前 Head Codex Review；当任一声明 Change 的 Profile 为 `high-risk` 时，还必须存在一个非作者、非 Bot、非配置 AI Actor 的当前 Head `APPROVED` Review。
#### Scenario SCN-GOV-MIN-004-01 普通 Change 保持效率
- Given: PR 只声明 lightweight 或 standard Change
- When: 当前 Head 已获得配置的 Codex Review 且线程已解决
- Then: 不额外要求人类 APPROVED
#### Scenario SCN-GOV-MIN-004-02 high-risk 人类批准
- Given: PR 声明至少一个 high-risk Change
- When: 只有 Codex、Bot、作者或旧 Head 的批准
- Then: PR Governance 失败，直到非作者人类在当前 Head 提交 APPROVED
#### Scenario SCN-GOV-MIN-004-03 后续请求修改
- Given: 人类 Reviewer 先批准当前 Head，随后又提交 CHANGES_REQUESTED
- When: PR Governance 读取该 Reviewer 最新状态
- Then: 旧批准失效并阻断合入

## MODIFIED

## SPEC-GOV-MIN-005 Release Evidence 支持同一 PR 完成状态闭环
#### Requirement
Release Evidence 应绑定最终 PR Head、Repository Validation、PR Governance 和注册测试结果，不要求在合入前记录尚未产生的 Merge SHA；满足 Release Approval 后可在同一个实现 PR 中将 Change 更新为 completed。
#### Scenario SCN-GOV-MIN-005-01 单 PR 收口
- Given: 最终 Head 的 Task、注册测试、Repository Validation、Review 和 Release Approval 均已完成
- When: Contributor 在同一实现 PR 中把 Change 更新为 completed
- Then: 门禁允许该 PR 直接合入，不要求额外 post-merge 状态收口 PR
