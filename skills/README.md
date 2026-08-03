# Skills

Skill 是可复用、可验证的 AI 执行单元。

## 两种层级

### Agent Skills 兼容层

最小要求为带 YAML frontmatter 的 `SKILL.md`，可通过 skills CLI 安装到 Claude Code、Codex 等 Agent。

### 项目增强层

复杂或高风险 Skill 可继续增加：

```text
manifest.yaml  输入、输出、依赖、读写权限和完成条件
templates/     产物模板
references/    必读规范
scripts/       确定性生成或校验脚本
examples/      正例、反例和边界案例
evals/         Skill 自身效果验证
```

## 目录

- `engineering/`：需求开发、TDD、实现、调试和评审 Skill；
- `upstream/`：上游来源、版本和许可证，不参与自动执行；
- 其他根级 Skill：本项目原生 OpenSpec 工件生成与验证能力。

项目适配 Skill 优先于上游同名 Skill。安装说明见 `INSTALL.md`。
