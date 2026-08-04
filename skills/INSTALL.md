# Install Project Skills

在仓库根目录安装本项目 Skill：

```bash
npx skills@latest add ./skills -a claude-code -a codex
```

需要复制文件而不是创建链接时：

```bash
npx skills@latest add ./skills -a claude-code -a codex --copy
```

项目内 Skill 已适配 `domains/`、`changes/` 和 `decisions/`，不要再安装上游同名 Skill 覆盖它们。
