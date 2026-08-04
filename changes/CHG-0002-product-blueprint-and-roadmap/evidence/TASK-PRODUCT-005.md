# TASK-PRODUCT-005 Evidence

- 产品定位、能力地图、Roadmap和Decision已建立双向关联。
- CHG-0002包含Proposal、Product Spec、Design、Tasks和Evidence。
- 自动校验命令：`python tools/validate_repo.py`。
- 回归测试命令：`python -m unittest discover -s tools/tests -p 'test_*.py'`。
- 最终GitHub Actions结果记录在 `repository-validation.md` 和 `release-approval.md`。
