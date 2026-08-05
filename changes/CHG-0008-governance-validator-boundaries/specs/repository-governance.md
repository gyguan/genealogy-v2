# Repository Governance Spec Delta

## MODIFIED

## SPEC-GOV-BOUNDARY-001 Decision 范围校验必须使用 canonical 类型与正确版本内容
#### Requirement
PR 范围校验必须以仓库正式 Decision schema 为准，并根据文件状态从 PR Head 或 Base 读取元数据；只有 `decisions/DEC-*.md` 作为正式 Decision 解析，支持文档按治理文档处理。
#### Scenario SCN-GOV-BOUNDARY-001-01 canonical Decision 类型
- Given: Decision 类型为 product、domain、architecture 或 compliance
- When: 计算该文件所需 Change 类型
- Then: 分别映射为 product、domain、engineering 或 governance/security，且不接受仓库 schema 之外的 Decision 类型
#### Scenario SCN-GOV-BOUNDARY-001-02 重命名或删除 Decision
- Given: PR 重命名或删除正式 Decision，旧路径仅存在于 Base
- When: 执行在线 PR 范围校验
- Then: 校验器从 Base SHA 读取旧文件元数据，并同时验证重命名前后的范围，不因旧路径在 Head 不存在而失败
#### Scenario SCN-GOV-BOUNDARY-001-03 Decision 支持文档
- Given: PR 修改 `decisions/README.md` 或其他非 `DEC-*.md` 支持文档
- When: 执行在线 PR 范围校验
- Then: 文件按 governance 文档分类，不要求 Decision Frontmatter

## SPEC-GOV-BOUNDARY-002 Spec 示例不得计入正式需求结构
#### Requirement
strict Spec 校验在识别 Action、Spec、Requirement 与 Scenario 前必须屏蔽 fenced Markdown 代码块，包括未闭合围栏到文件末尾的内容。
#### Scenario SCN-GOV-BOUNDARY-002-01 fenced Spec 示例
- Given: 合法 Spec 正文包含 fenced 代码示例，示例内出现 `## SPEC-*` 或 `#### Scenario SCN-*`
- When: 执行 strict Change 质量校验
- Then: 示例中的标题不生成正式 Spec/Scenario，不截断真实 Requirement，也不参与 Task/Test 追踪

## SPEC-GOV-BOUNDARY-003 Design 段落状态必须符合 CommonMark 边界
#### Requirement
Design 可见内容解析必须区分可中断开放段落的块标记与仅在新块起点有效的标记，并保持带正文列表项的段落打开状态。
#### Scenario SCN-GOV-BOUNDARY-003-01 非 1 有序标记保持在 lazy quote
- Given: 引用段落后无空行出现以 `2.` 或 `2)` 开头的 lazy continuation
- When: 执行 Design Contract 校验
- Then: 该行仍被视为引用内容，不能用其中的稳定 ID 满足 required facet
#### Scenario SCN-GOV-BOUNDARY-003-02 列表项正文保持开放段落
- Given: 带正文的列表项后出现不能中断段落的 type-7 HTML 标签及稳定 ID
- When: 执行 Design Contract 校验
- Then: 标签与后续文本保持可见，合法稳定 ID 不被错误屏蔽
