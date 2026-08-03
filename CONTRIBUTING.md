# 贡献规则

## 基本流程

```text
创建 Change
→ 生成 Proposal / Specs / Design / Tasks
→ 自动校验
→ 人工评审
→ 生成开发任务包
→ 实现与验证
→ 合入基线
→ 归档 Change
```

## 目录原则

- 正式产品目标进入 `product/`。
- 稳定领域语义进入 `domains/`。
- 单次增量只进入 `changes/active/`。
- 长期决策进入 `decisions/`。
- 非权威研究进入 `reference/`。
- 验证标准进入领域内 Eval 或根 `evals/`。

禁止使用 `final-v2`、`latest`、`new` 等相对文件名。
