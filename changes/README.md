# Changes

Change 是单次增量需求、设计、任务、Gate 与证据的事实源。使用：

```bash
python tools/new_change.py CHG-0010 stable-name --type engineering --issue 15
python tools/context.py CHG-0010 --bundle
python tools/check.py
```

Profile：`lightweight` 用于低风险文案/机械修改；`standard` 用于普通工程需求；`high-risk` 用于产品、领域、安全、权限、迁移等。产品、领域和安全 Change 必须为 high-risk，治理 Change 不得为 lightweight。

新 Change 默认启用 `quality_policy: strict`：Proposal 与 Design 必须有有效正文；Spec 使用 ADDED/MODIFIED/REMOVED/RENAMED、稳定 SPEC ID 和可观察 Scenario；Task 必须覆盖 Spec/Scenario；`tests.yaml` 注册真实 Test ID、命令和 Spec 映射。PR 中只执行 Body 明确声明 Change 的注册命令，使用受控 Runner、超时和无 GitHub Token 的最小环境，不重放全部历史 Change。

从 `CHG-0007` 起继续维护 Design Contract v1 的 `design.md` Frontmatter 与八个固定章节。从 `CHG-0009` 起还必须维护 `design.yaml`：它是引用、facet、FACT/ASM/OPEN、Definition 和 Spec/Test Traceability 的机器事实源；`design.md` 只负责解释方案、流程、失败、风险和权衡。

`new_change.py` 会按 Change 类型初始化机器 facet：确定必需项直接标记 `required`，其余项使用 `review-required`。进入 Review 前必须收敛全部 `review-required`、关闭阻断假设和开放问题、替换模板占位 ID，并运行独立 `design-review`。

PR 修改正式 Domain、Decision 或 Capability 时，实际变化 ID 必须出现在 Change 的 `affected_domains`、`affected_decisions` 或 `capabilities` 中。该规则不要求普通代码文件逐一映射 Task，避免不必要的维护负担。

校验结果分为：

- Error：客观错误并阻断；
- Warning：历史迁移或疑似风险，进入评审但不自动裁决；
- Review-only：业务正确性、领域语义、方案取舍、风险接受和测试充分性。

lightweight 与 standard 维持当前 Head Codex Review；high-risk 还必须获得非作者人类在当前 Head 的 APPROVED。

批准 Gate 必须记录来源与引用。进入完成态前，Task、Evidence、Release Gate、最终 Head Review、设计契约、注册测试和 CI 必须一致。Release Evidence 绑定最终 PR Head、Repository Validation、PR Governance 和注册测试结果，不要求合入前记录尚未产生的 Merge SHA；满足条件后可在同一个实现 PR 中更新 completed，不需要额外 post-merge 收口 PR。
