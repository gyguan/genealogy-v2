# Design
## 方案概览
新增轻量 `diagnostics.py` 作为统一诊断模型；`validate_change_quality.py` 负责本地内容与追踪校验；`validate_pr_change.py` 负责 GitHub PR 在线范围校验。Error 决定退出码，Warning 和 Review-only 只进入报告。
## 领域与数据影响
不修改业务领域数据。新增 Change 元数据 `quality_policy: strict` 和每个 Change 的 `tests.yaml` 测试注册表，历史 Change 保持兼容。
## 接口与模块边界
`diagnostics.py` 只提供诊断数据结构与报告器；本地校验器只读取仓库文件；PR 校验器通过 GitHub REST API 读取 PR、Changed Files 和 Issue，不写远端状态。
## 安全与隐私
只处理公开仓库元数据和治理文件，不读取或输出族人敏感信息。GitHub Token 仅使用只读权限。
## 测试 Seam
核心解析和范围判断均设计为纯函数；回归测试通过复制仓库、注入反例并执行校验脚本，在线 API 主流程在无 PR 环境时安全跳过。
## 失败、补偿与回滚
任何 Error 返回非零退出码并阻断 CI；Warning 与 Review-only 返回零。若新规则误报，可删除对应校验器入口并保留历史 Change 数据，不影响现有业务资产。
## 迁移方案
新建 Change 默认 strict；历史 Change 未启用 strict 时输出迁移 Warning，不要求一次性重写。后续可逐个 Change 升级。
## 备选方案与权衡
未选择把所有质量要求写进 `validate_repo.py`，避免单文件继续膨胀和规则耦合；也未采用 LLM 自动裁决内容质量，因为结果不具备确定性和可重复性。
