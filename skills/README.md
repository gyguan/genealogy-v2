# Skills

本目录存放项目适配后的 AI 需求开发 Skill。每个直接子目录使用一个带 YAML frontmatter 的 `SKILL.md`，由 Agent Skills 机制自动发现，不额外维护 Skill Catalog。

推荐流程：

```text
grill-with-docs
→ domain-modeling
→ to-spec
→ openspec-validation
→ design-review（独立上下文）
→ to-tickets
→ implement + tdd
→ code-review
```

`upstream/` 只保存来源、固定版本和许可证，不参与自动执行。
