# Changes

每个非平凡需求使用一个稳定目录：

```text
changes/CHG-xxxx-name/
├── change.yaml
├── proposal.md
├── specs/
├── design.md
├── tasks.md
└── evidence/
```

状态只记录在 `change.yaml` 中，不通过 `active/`、`archived/` 移动目录表达状态，以保证 Issue、PR 和文档链接长期稳定。
