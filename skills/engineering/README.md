# Engineering Skills

本目录将 Matt Pocock 的工程实践适配到 Genealogy V2 的 OpenSpec、领域资产和验证体系。

## 标准链路

```text
setup-genealogy-skills
→ grill-with-docs / domain-modeling
→ to-spec
→ to-tickets
→ implement + tdd
→ code-review
```

Bug 使用 `diagnosing-bugs` 建立可重复反馈闭环；模块边界和测试 Seam 使用 `codebase-design`。

## 适配原则

- `domains/` 代替上游默认的 `CONTEXT.md`；
- `decisions/` 代替上游默认的 `docs/adr/`；
- `changes/` 中 OpenSpec 是需求事实源；
- GitHub Issues 是 Ticket 执行视图；
- `evals/` 和 Change `evidence/` 是完成证据；
- 任何同名上游 Skill 都不得覆盖本目录版本。
