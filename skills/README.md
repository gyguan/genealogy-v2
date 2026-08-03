# Skills

Skill 是可复用、可验证的 AI 执行单元。

每个 Skill 应包含：

```text
SKILL.md       目标、适用条件和执行步骤
manifest.yaml  输入、输出、依赖、读写权限和完成条件
templates/     产物模板
references/    必读规范
scripts/       确定性生成或校验脚本
examples/      正例、反例和边界案例
evals/         Skill 自身效果验证
```

当前只创建核心 OpenSpec 流程 Skill 的说明骨架，待实际实现时再补充脚本和 Eval。
