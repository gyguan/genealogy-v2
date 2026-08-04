# 产品能力文件

本目录按能力组维护正式产品能力，避免单个超大 YAML 文件成为 AI 和协作瓶颈。

每个文件只包含一个能力组。全局文件清单和规则位于 `../capability-map.yaml`，版本定义位于 `../releases.yaml`。Manifest 不得重复维护 Capability 名称、分组或领域投影。

## 字段含义

- `capability_type`：`business`、`application` 或 `platform`；
- `primary_domain`：产品责任主领域，不等同于代码归属；
- `supporting_domains`：共同提供语义或数据的领域；
- `platform_area`：平台能力所属技术治理范围；
- `target_release`：当前最早目标版本；
- `release_priority`：目标版本内的 `must`、`should` 或 `could`；
- `status`：`candidate`、`planned`、`in-progress`、`delivered` 或 `deprecated`；
- `planning_confidence`：`high`、`medium` 或 `low`；
- `depends_on`：产品能力依赖，不直接代表代码依赖。

能力的拆分、合并、改名、版本调整和废弃必须通过批准的产品 Change。
