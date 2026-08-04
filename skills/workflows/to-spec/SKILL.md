---
name: to-spec
description: Turn the requirement discussion into an OpenSpec Change.
disable-model-invocation: true
---

# To Spec

1. 用 `tools/new_change.py` 创建 Change。
2. 更新 `change.yaml` 和 `context.md`。
3. 生成 `proposal.md`、按领域拆分的 `specs/`、`design.md`。
4. 在 `implementation/seams.yaml` 记录最高可行测试 Seam。
5. 调用 `openspec-validation`。Spec 批准前不得生成代码。
