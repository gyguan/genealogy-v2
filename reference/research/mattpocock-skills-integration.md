# Matt Pocock Skills Integration

## 采用原因

上游 Skill 强调需求对齐、统一领域语言、纵向切片、快速反馈、TDD、深模块和双轴代码评审，适合约束 AI 生成代码的常见失效模式。

## 本地适配

| 上游约定 | Genealogy V2 适配 |
|---|---|
| `CONTEXT.md` | `domains/glossary.yaml` + 相关领域资产 |
| `docs/adr/` | `decisions/` |
| Spec 直接进入 Issue | OpenSpec Change 为事实源，Issue 为执行视图 |
| Ticket | `tasks.md` + `tracer-tickets.yaml` + 可选 GitHub Issue |
| 测试 Seam 口头确认 | `implementation/seams.yaml` 固化 |
| Review 输出到会话 | `reviews/code-review.md` 留存 |

## 更新策略

- 上游固定到 `skills/upstream/mattpocock/source.yaml` 中的 commit；
- 定期比较上游变化，人工选择性合并；
- 不自动覆盖项目适配内容；
- 更新后必须执行 Skill Eval 和至少一个真实 Change 演练。
