# AI 导航层

本目录定义 AI 如何找到最小充分上下文、选择 Skill 和解释兼容资产，不存放业务事实。

- `repo-map.yaml`：权威入口；
- `context-packs/`：任务所需的最小上下文；
- `routing/`：任务状态到 Skill 的机器路由；
- `policies/`：指令、修改和人工门禁策略；
- `adapters/`：外部 Agent 约定到本仓结构的映射。
