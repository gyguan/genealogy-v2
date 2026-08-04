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

Change 使用 `product`、`domain`、`engineering`、`governance` 或 `security` 类型；只有产品和领域 Change 强制关联产品能力。

状态只记录在 `change.yaml` 中，不通过移动目录表达状态，以保证 Issue、PR 和文档链接长期稳定。

## 状态与 Gate

| 状态 | 必须满足 |
|---|---|
| `draft` | 可处于澄清和初稿阶段 |
| `review` | 受影响范围和真实 Spec 已明确，Spec Gate 为 `pending` 或 `approved` |
| `approved` | Spec Gate 已批准，Design 和 Task 已准备 |
| `implementing` | Spec 与 Implementation Gate 已批准 |
| `completed` | 三个 Gate 均批准、Task 全部完成、Evidence 完整 |
| `cancelled` | 必须记录取消原因 |

Gate 使用 `blocked`、`pending`、`approved` 或 `rejected`。批准的 Gate 必须记录批准人、时间和证据路径。
