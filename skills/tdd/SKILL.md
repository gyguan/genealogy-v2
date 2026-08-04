---
name: tdd
description: Implement behavior through a red-green-refactor loop at an approved public test Seam.
---

# TDD

1. Add one failing test for an approved acceptance behavior.
2. Confirm the failure proves missing behavior rather than a broken test.
3. Add the minimum implementation to make it pass.
4. Refactor without changing observable behavior.
5. Run relevant regression tests and record commands and results.

Do not test private implementation details or replace meaningful behavior with excessive mocks.
