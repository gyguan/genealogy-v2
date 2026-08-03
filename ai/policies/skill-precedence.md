# Skill Precedence

项目 Skill 是对上游工程方法的本地适配，不是简单镜像。

优先级：

1. 用户当前明确要求；
2. 根 `AGENTS.md`；
3. 当前 Change 的 `context.yaml`；
4. 正式领域规则和 Decision；
5. `skills/engineering/` 中的项目适配 Skill；
6. `mattpocock/skills` 等外部 Skill；
7. `reference/` 中的研究和示例。

当上游 Skill 提到 `CONTEXT.md` 时，本项目读取 `domains/glossary.yaml`、`domains/context-map.yaml` 和相关领域目录。

当上游 Skill 提到 `docs/adr/` 时，本项目读取和写入 `decisions/`，并遵循 Decision 模板。

当上游 Skill 要把 Spec 直接写入 Issue 时，本项目先写入 `changes/active/<change-id>/`；GitHub Issue 仅承载执行摘要和链接。
