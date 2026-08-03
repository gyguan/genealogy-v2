# API 设计规范

> 状态：Review

## 1. 目标

API 是业务契约，不是数据库表的远程 CRUD 包装。

接口必须：

- 使用业务语言表达用例；
- 明确区分查询、草稿和正式变更；
- 支持权限、隐私、并发和幂等校验；
- 为前端提供可直接展示的读模型；
- 不暴露旧系统兼容包袱；
- 只有真实用例进入实施时才纳入公共契约。

## 2. Contract First

公共接口变更顺序：

```text
用例与验收标准
  → 领域命令 / 查询语义
  → OpenAPI 契约
  → 契约评审
  → 后端实现
  → 前端生成类型与实现
  → 契约、集成和端到端验证
```

禁止先写 Controller，再根据实现补文档。

## 3. 版本与路径

首个正式版本统一使用：

```text
/api/v2
```

版本号表达破坏性公共契约边界，不用于每个内部模块单独演进。

推荐路径：

```text
/api/v2/clan-spaces/{clanSpaceId}/persons
/api/v2/clan-spaces/{clanSpaceId}/lineage-units
/api/v2/clan-spaces/{clanSpaceId}/family-unions
/api/v2/clan-spaces/{clanSpaceId}/sources
/api/v2/clan-spaces/{clanSpaceId}/change-requests
```

宗族空间出现在路径中，用于表达租户和授权边界；服务端仍必须校验当前用户是否属于该空间。

## 4. 查询与命令分离

### 查询接口

使用 `GET`，返回用途明确的读模型。

示例：

```text
GET /persons/{personId}
GET /persons?name=&lineageUnitId=&status=
GET /graphs/lineage?rootPersonId=&depth=
GET /change-requests?queue=assigned-to-me
```

### 草稿接口

低风险、尚未进入正式事实流程的内容可以使用资源式草稿接口。

示例：

```text
POST /drafts/sources
PATCH /drafts/sources/{sourceId}
```

草稿接口不得被正式图谱、公开档案和对外导出当作正式事实。

### 正式变更命令

正式事实变化使用业务命令，不使用泛化 PATCH。

示例：

```text
POST /change-requests/person-name-corrections
POST /change-requests/lineage-membership-transfers
POST /change-requests/parent-child-establishments
POST /change-requests/lineage-unit-splits
POST /change-requests/succession-arrangements
```

命令名称应反映用户意图，而不是表操作。

## 5. 标识与引用

- 公共对象使用不可推断的稳定标识，优先 UUID；
- 普通页面不展示技术标识；
- API 中跨对象引用使用类型明确的字段，例如 `personId`、`sourceId`；
- 禁止使用核心通用结构：

```json
{
  "targetType": "...",
  "targetId": "..."
}
```

只有审计检索等不承担完整性责任的辅助场景才可使用通用引用，并必须标明用途边界。

## 6. 命令信封

正式变更请求至少包含：

```json
{
  "commandVersion": 1,
  "idempotencyKey": "客户端生成的稳定值",
  "expectedVersions": [
    { "resourceType": "PERSON", "resourceId": "...", "version": 7 }
  ],
  "reason": "业务说明",
  "payload": {}
}
```

服务端补充并固化：

- 提交人；
- 宗族空间；
- 授权范围；
- 规范化载荷摘要；
- 提交时间；
- 处理器版本。

相同幂等键必须对应相同规范化载荷；不一致时返回冲突，不覆盖原命令。

## 7. 并发控制

正式资源使用显式版本号。

写命令提交预期资源版本，执行前再次验证。

冲突返回：

```text
409 RESOURCE_VERSION_CONFLICT
```

响应应包含：

- 冲突资源的业务类型；
- 客户端预期版本；
- 当前版本；
- 建议动作：刷新、比较或重新提交。

不使用“最后写入覆盖”处理正式事实冲突。

## 8. 状态码

| 状态码 | 用途 |
|---|---|
| 200 | 成功查询或同步操作成功 |
| 201 | 创建草稿、任务或变更请求 |
| 202 | 已接受异步导入、导出或大型投影任务 |
| 204 | 无响应体的成功操作 |
| 400 | 请求结构或基础校验错误 |
| 401 | 未认证 |
| 403 | 已认证但无权访问或操作 |
| 404 | 对象不存在，或出于隐私策略不可暴露其存在 |
| 409 | 版本、幂等、状态或业务冲突 |
| 422 | 结构合法但违反领域规则 |
| 429 | 频率或资源限制 |
| 500 | 未预期服务端错误 |
| 503 | 依赖服务暂不可用 |

## 9. 统一错误结构

```json
{
  "code": "LINEAGE_CYCLE_DETECTED",
  "message": "调整后会形成谱系组织循环",
  "requestId": "...",
  "details": [
    {
      "field": "newParentLineageUnitId",
      "reason": "目标节点位于当前节点子树中"
    }
  ],
  "actions": ["CHOOSE_ANOTHER_PARENT"]
}
```

要求：

- `code` 稳定，可用于前端映射；
- `message` 使用业务语言；
- `details` 不包含 SQL、类名或堆栈；
- `requestId` 支持审计和排障；
- 生产环境不返回敏感数据。

## 10. 分页与排序

普通管理列表首期使用基于页码或游标的统一方案，不在不同模块随意混用。

分页响应至少包含：

```json
{
  "items": [],
  "page": 1,
  "pageSize": 20,
  "total": 125,
  "hasNext": true
}
```

要求：

- `pageSize` 有默认值和硬上限；
- 排序字段采用允许列表；
- 始终包含稳定次级排序，例如对象 ID；
- 不允许客户端传任意 SQL 字段名；
- 大规模导出不通过无限分页接口完成。

## 11. 图谱查询

图谱查询必须声明限制：

- 起始人物或组织；
- 图谱类型；
- 深度；
- 最大节点数；
- 最大边数；
- 是否包含历史或争议信息；
- 是否发生截断。

响应示例结构：

```json
{
  "graphType": "LINEAGE",
  "nodes": [],
  "edges": [],
  "limits": {
    "depth": 5,
    "maxNodes": 500,
    "maxEdges": 1000
  },
  "truncated": false
}
```

节点和边使用图谱用途明确的 DTO，不复用数据库实体或万能关系 DTO。

## 12. 日期和时间

- 系统时间使用 ISO 8601，传输时带时区或使用 UTC；
- 历史日期使用结构化对象表达精度、约略、区间和原文；
- 不把不精确历史日期压缩为虚构的 `YYYY-MM-DD`；
- API 字段必须区分 `effectiveTime` 和 `recordedAt` 等不同语义。

历史日期示例：

```json
{
  "precision": "YEAR",
  "year": 1876,
  "approximate": true,
  "originalText": "约光绪二年"
}
```

## 13. 权限和隐私响应

后端返回最终可见内容和允许动作：

```json
{
  "person": {},
  "permissions": {
    "canViewSensitiveFields": false,
    "canProposeChange": true,
    "canReview": false
  },
  "redactions": ["CONTACT", "EXACT_ADDRESS"]
}
```

前端不得通过重新请求、拼接其他接口或缓存旧数据绕过裁剪。

对无权知道对象是否存在的场景返回 404，而不是泄漏存在性的 403。

## 14. 审核接口

审核操作使用明确动作：

```text
POST /change-requests/{id}/submit
POST /change-requests/{id}/approve
POST /change-requests/{id}/reject
POST /change-requests/{id}/request-changes
POST /change-requests/{id}/execute
```

实际是否允许自动执行由策略决定。

审核响应必须包含新的状态和版本，客户端不得乐观猜测状态。

## 15. 导入与导出

导入流程：

```text
创建批次 → 上传 → 解析 → 校验 → 预览 → 确认 → 生成草稿或变更请求 → 审核生效
```

导出流程：

```text
创建任务 → 冻结查询条件和权限快照 → 生成 → 安全下载 → 到期清理
```

要求：

- 导入不能直接写正式事实；
- 导出必须按字段级隐私裁剪；
- 任务接口返回进度、错误摘要和可恢复动作；
- 文件下载使用短期授权，不暴露存储路径。

## 16. 契约验收

每个新增接口至少具备：

- 明确用户用例；
- 请求和响应示例；
- 权限和隐私规则；
- 领域错误清单；
- 幂等与并发策略；
- 分页或结果上限；
- OpenAPI 校验；
- 后端契约测试；
- 前端生成类型校验；
- 至少一条关键端到端场景。
