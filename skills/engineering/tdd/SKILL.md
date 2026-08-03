---
name: tdd
description: Implement one vertical slice at a time through a pre-agreed public test seam using red-green cycles.
---

# Test-Driven Development

1. Read `implementation/seams.yaml`; do not invent an unapproved Seam.
2. Test observable behavior through public interfaces, never private methods or internal collaboration details.
3. Work one tracer slice at a time: one failing test, minimal implementation, then the next test.
4. Watch the test fail for the expected reason before writing production code.
5. Expected values must come from the Spec, a worked example or another independent source of truth.
6. Avoid tautological tests, implementation-coupled mocks and horizontal batches of imagined tests.
7. Run focused tests frequently and the full relevant suite before completion.
8. Store commands and results under Change `evidence/test-results/`.
9. Structural refactoring belongs in review unless required to expose the approved Seam.
