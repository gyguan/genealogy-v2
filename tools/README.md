# Repository Tools

- `new_change.py`：从模板创建稳定的 Change 目录，并阻止 Change ID 重复使用；
- `validate_repo.py`：校验产品能力、术语、领域依赖、Decision、Change Gate、Spec/Task/Evidence 追踪和 Skill 可发现性；
- `tests/test_validate_repo.py`：保存仓库校验器的正向与关键反例回归测试。

本地和 CI 使用相同入口：

```bash
python tools/validate_repo.py
python -m unittest discover -s tools/tests -p 'test_*.py'
```
