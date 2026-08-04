# Install Project Skills

在仓库根目录安装项目 Skill：

```bash
npx skills@latest add ./skills/workflows -a claude-code -a codex
npx skills@latest add ./skills/disciplines -a claude-code -a codex
npx skills@latest add ./skills/validators -a claude-code -a codex
```

不要再次安装上游同名 Skill，以免覆盖本仓 OpenSpec 和领域适配。首次运行 `/setup-genealogy-skills`。
