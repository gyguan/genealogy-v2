# Genealogy V2

面向中国式商用族谱系统的 AI 辅助研发项目。

## AI 开发入口

```bash
python tools/new_change.py CHG-0006 stable-name --type engineering --issue 8
python tools/context.py CHG-0006
python tools/check.py
```

读取 `AGENTS.md` 与 `SECURITY.md`，以 Change 为工作入口，由 `context.py` 输出最小上下文。产品能力按组维护，不读取全量重复投影。

## 流程
`grill-with-docs → domain-modeling → to-spec → openspec-validation → review → to-tickets → implement+tdd → code-review → check`

## 核心目录
`product/` 产品版本与分组能力；`domains/` 领域事实；`changes/` 增量事实；`decisions/` 长期决策；`skills/` 方法；`tools/` 自动化与门禁；`.github/` PR、CI 与规则配置。
