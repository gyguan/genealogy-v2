# Repository Tools

- `new_change.py`：从模板创建稳定的 Change 目录，并阻止 Change ID 重复使用；
- `validate_repo.py`：校验术语、领域依赖、Decision、Change Gate、Spec/Task/Evidence追踪和Skill可发现性；
- `validate_product.py`：校验版本、分片产品能力、依赖顺序和Roadmap语义完整性；
- `tests/test_validate_repo.py`：保存仓库校验器的正向与关键反例回归测试。

产品校验重点包括：Manifest与能力文件清单一致；Release、Capability和Group ID唯一；能力类型、责任领域、版本、状态、承诺级别和规划置信度合法；Capability依赖无未知引用、无循环、无版本倒挂；V0.1—V0.5 Roadmap具备纵向闭环、非目标、验收、成功指标和风险。

本地和CI使用相同入口：

```bash
python tools/validate_repo.py
python tools/validate_product.py
python -m unittest discover -s tools/tests -p 'test_*.py'
```
