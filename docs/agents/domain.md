# Domain Docs

本仓库采用多领域上下文，不使用上游默认的单一 `CONTEXT.md` 布局。

## 必读资产

- `domains/glossary.yaml`：全仓统一业务语言；
- `domains/context-map.yaml`：领域边界和依赖；
- `domains/<domain>/README.md`：领域职责与非职责；
- `domains/<domain>/model/`、`rules/`、`evals/`：领域事实、不变量和验证；
- `decisions/`：长期产品、领域和架构决策。

## 使用规则

- 输出中的类名、方法名、测试名和 Ticket 标题使用统一领域术语。
- 新术语不得只存在于代码或 Change 中，必须通过 `domain-modeling` 固化。
- 领域文档不写具体框架、文件路径和实现细节。
- 与现有 Decision 冲突时必须显式指出，不得静默覆盖。
