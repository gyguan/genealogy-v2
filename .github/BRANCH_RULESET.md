# Main Branch Ruleset

在 GitHub Settings → Rules → Rulesets 为 `main` 配置：

- 仅允许通过 Pull Request 合入，禁止直接 Push、Force Push 和删除；
- 合入前分支必须与主分支保持最新；
- Required checks：`repository-validation`、`pr-governance`；
- 必须解决全部 Review Conversation；
- 新提交使旧批准失效；
- 至少一个独立 Reviewer；
- 管理员不设置长期绕过，仅允许审计化的紧急临时绕过。

仓库内校验无法替代 GitHub 服务端 Ruleset；启用后以仓库设置为最终强制门禁。
