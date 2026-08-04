# Design

## 方案概览

保留现有七类核心资产，以 `AGENTS.md` 明确权威层级，以 YAML Frontmatter 和统一 Markdown 标记提供轻量机器可读性，并增强单一 Python 校验入口。

## 领域与数据影响

`domains/context-map.yaml` 成为领域依赖唯一事实源，依赖增加类型并补齐项目编排、证据和出版快照关系。领域文件只维护职责、非职责和不变量。Capability 与 Glossary 填充首批稳定 ID。

## 接口与模块边界

本 Change 不创建代码模块。`DEC-0001` 决定未来采用 `apps/modules/platform/contracts/tests` 的领域对齐模块化单体，并禁止根级技术分层和无约束共享目录。

## 安全与隐私

修正规则优先级，确保 SECURITY、全局红线、正式不变量和 Accepted Decision 高于临时任务要求；不引入真实族人数据。

## 测试 Seam

公共测试 Seam 为 `python tools/validate_repo.py` 的退出码和错误列表。正向仓库必须返回 0，构造的非法状态、引用和依赖样本必须返回非 0。

## 失败、补偿与回滚

若校验器误阻断合理变更，可回滚对应规则，或通过新的 Change 与 Decision 扩展合法目录和状态，而不是绕过 CI。

## 迁移方案

现有领域 Frontmatter 删除 `depends_on`，依赖集中迁移到 Context Map；Change 模板升级为对象化 Gate；旧 Change 尚不存在，无批量迁移成本。

## 备选方案与权衡

未恢复复杂 `ai/`、`schemas/`、`evals/` 和 `knowledge/` 层；当前规模优先使用轻量约定和确定性脚本，真实需求出现后再演进。
