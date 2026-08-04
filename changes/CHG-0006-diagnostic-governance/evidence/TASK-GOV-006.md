# TASK-GOV-006 Evidence

- Specs: SPEC-GOV-007
- Scenarios: SCN-GOV-007-01, SCN-GOV-007-02
- Implementation baseline: `68a246ffced8f0a9644e6b5cd428ea39b0c5d66b`
- GitHub Actions run: `30887566862`
- Check: `python tools/check.py`
- Result: success

`tools/diagnostics.py` 已实现 Error、Warning、Review-only 数据结构、分级报告和退出码。回归测试验证 Warning 不改变成功退出码，Error 会阻断校验。
