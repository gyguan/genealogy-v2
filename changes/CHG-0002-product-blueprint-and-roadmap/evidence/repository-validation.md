# Repository Validation Evidence

## Commands

```bash
python tools/validate_repo.py
python -m unittest discover -s tools/tests -p 'test_*.py'
```

## Expected Results

- Capability、Decision、Change、Spec、Task和Evidence引用有效；
- 仓库校验退出码为0；
- 回归测试全部通过；
- GitHub Actions运行结果将在PR校验后补充。
