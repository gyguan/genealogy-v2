# Changes

Change 是单次增量需求、设计、任务、Gate 与证据的事实源。使用：

```bash
python tools/new_change.py CHG-0009 stable-name --type engineering --issue 15
python tools/context.py CHG-0009 --bundle
python tools/check.py
```

Profile：`lightweight` 用于低风险文案/机械修改；`standard` 用于普通工程需求；`high-risk` 用于产品、领域、安全、权限、迁移等。产品、领域和安全 Change 必须为 high-risk，治理 Change 不得为 lightweight。

新 Change 默认启用 `quality_policy: strict`：Proposal 与 Design 必须有有效正文；Spec 使用 ADDED/MODIFIED/REMOVED/RENAMED、稳定 SPEC ID 和可观察 Scenario；Task 必须覆盖 Spec/Scenario；`tests.yaml` 注册真实 Test ID、命令和 Spec 映射。

从 `CHG-0007` 起继续维护 Design Contract v1 的 `design.md` Frontmatter 与八个固定章节。从 `CHG-0008` 起还必须维护 `design.yaml`：它是引用、facet、FACT/ASM/OPEN、Definition 和 Spec/Test Traceability 的机器事实源；`design.md` 只负责解释方案、流程、失败、风险和权衡。

`new_change.py` 会按 Change 类型初始化机器 facet：确定必需项直接标记 `required`，其余项使用 `review-required`。进入 Review 前必须收敛全部 `review-required`、关闭阻断假设和开放问题，并运行独立 `design-review`。

校验结果分为：

- Error：客观错误并阻断；
- Warning：历史迁移或疑似风险，进入评审但不自动裁决；
- Review-only：业务正确性、领域语义、方案取舍、风险接受和测试充分性。

批准 Gate 必须记录来源与引用。进入完成态前，Task、Evidence、Release Gate、最终 Head Review、设计契约和 CI 必须一致。
