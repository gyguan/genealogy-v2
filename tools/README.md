# Repository Tools

- `new_change.py`：参数化创建 strict Change，校验 Capability、Domain、Decision，并生成 Spec、Task、Test 骨架；
- `context.py`：根据 Change 生成 AI 和贡献者所需的最小文件清单；
- `diagnostics.py`：统一 Error、Warning、Review-only 数据结构、报告和退出码；
- `validate_repo.py`：校验领域、Decision、Change Gate、Spec/Task/Evidence 与 Skill；
- `validate_product.py`：校验版本、分片能力、闭环引用、依赖顺序和 Roadmap；
- `validate_change_quality.py`：校验内容非空、strict Spec Scenario、Task/Test 双向追踪并输出人工评审清单；
- `validate_pr.py`：校验当前 Head 的独立评审信号和未解决 Review Thread；
- `validate_pr_change.py`：在线校验 PR 声明 Change、真实 Issue 和 Changed Files 范围；
- `check.py`：本地与 CI 唯一检查入口；
- `tests/`：保存正向与关键反例回归测试。

```bash
python tools/check.py
```

诊断分级：

- `ERROR`：客观错误，返回非零并阻断；
- `WARNING`：历史迁移或启发式风险，不直接阻断，但必须进入评审；
- `REVIEW`：业务正确性、领域语义、方案取舍、风险接受和测试充分性，只能由 Reviewer 判断。

`validate_repo.py` 只读取产品 Capability ID 供 Change 追踪；产品语义只由 `validate_product.py` 校验，避免两套校验重复扫描和规则漂移。PR 评审门禁由 GitHub Actions 执行，但必须配合 `.github/BRANCH_RULESET.md` 的服务端 Ruleset 才不可绕过。
