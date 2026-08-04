---
name: tdd
description: Develop one behavior slice using red-green TDD at an approved seam.
---

# TDD

测试公共行为而非实现细节。只在 `implementation/seams.yaml` 批准的 Seam 上测试。每轮一个失败测试、最小实现和证据；禁止批量先写想象中的测试，禁止通过降低断言变绿。
