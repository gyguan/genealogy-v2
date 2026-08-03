# Install Project Skills

## 推荐：安装本仓适配后的 Skill

在仓库根目录执行：

```bash
npx skills@latest add ./skills/engineering -a claude-code -a codex
```

需要复制而不是创建链接时：

```bash
npx skills@latest add ./skills/engineering -a claude-code -a codex --copy
```

安装后应优先使用本仓版本的 `grill-with-docs`、`domain-modeling`、`to-spec`、`to-tickets`、`implement`、`tdd`、`code-review`、`diagnosing-bugs` 和 `codebase-design`。

## 可选：安装上游其他 Skill

```bash
npx skills@latest add mattpocock/skills
```

交互选择时不要再次安装上述同名核心 Skill，以免覆盖项目适配。可以选择 `prototype`、`wayfinder`、`improve-codebase-architecture` 等尚未本地适配的能力。

## 首次使用

运行 `/setup-genealogy-skills` 检查 Agent 是否能读取：

- `AGENTS.md`
- `docs/agents/`
- `domains/`
- `changes/`
- `decisions/`
- `evals/`
