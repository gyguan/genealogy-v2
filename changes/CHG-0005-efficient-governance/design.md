# Design
## 方案概览
Manifest-only Capability、check.py、context.py、增强 new_change.py、validate_pr.py 和 GitHub workflow。
## 领域与数据影响
不改变领域模型或业务数据。
## 接口与模块边界
工具保持 Python 标准库加 PyYAML；CI 只调用统一入口。
## 安全与隐私
GITHUB_TOKEN 仅使用只读权限；不输出凭证。
## 测试 Seam
仓库、产品、工具和 PR 跳过路径回归测试。
## 失败、补偿与回滚
任一检查非零即阻断；可整体回滚。
## 迁移方案
旧 Change v1 继续兼容，新 Change 使用 v2。
## 备选方案与权衡
仅靠文档无法强制；采用轻量脚本而非平台化引擎。
