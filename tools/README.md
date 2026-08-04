# Repository Tools

- `new_change.py`：从简化模板创建稳定的 Change 目录；
- `validate_repo.py`：校验必要目录、领域文件、Change 工件和 Skill 可发现性。

本地和 CI 使用同一个校验入口：

```bash
python tools/validate_repo.py
```
