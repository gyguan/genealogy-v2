# Changes

Change 是单次增量需求、设计、任务、Gate 与证据的事实源。使用：

```bash
python tools/new_change.py CHG-0006 stable-name --type engineering --issue 8
python tools/context.py CHG-0006
python tools/check.py
```

Profile：`lightweight` 用于低风险文案/机械修改；`standard` 用于普通工程需求；`high-risk` 用于产品、领域、安全、权限、迁移等。产品、领域和安全 Change 必须为 high-risk，治理 Change 不得为 lightweight。

批准 Gate 必须记录来源与引用。进入完成态前，Task、Evidence、Release Gate、最终 Head Review 和 CI 必须一致。
