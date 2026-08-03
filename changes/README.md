# Changes

每个非平凡变更都必须建立独立目录，并原生采用 OpenSpec 工件：

```text
context.yaml
proposal.md
specs/
design.md
tasks.md
implementation/
validation/
reviews/
evidence/
```

## Skill 流转

- `grill-with-docs`：澄清需求并更新上下文；
- `to-spec`：生成 Proposal、Spec Delta、Design 和测试 Seam；
- `to-tickets`：生成纵向切片和阻塞关系；
- `implement` + `tdd`：逐 Ticket 实现并保存证据；
- `code-review`：输出 Standards 与 Spec 双轴报告。

- `active/`：正在设计、评审或实现的 Change；
- `archived/`：已经完成、取消或被替代的 Change；
- `_template/`：标准目录模板。
