---
name: openspec-validation
description: Validate an OpenSpec Change for completeness, consistency, testability and traceability.
---

# OpenSpec Validation

Check that:

- goal, non-goals and affected domains are explicit;
- each requirement has a stable ID and observable acceptance scenario;
- Design addresses domain, data, interface, privacy, failure and migration impact;
- each Task traces to one or more Spec IDs;
- tests use a stable public Seam;
- no unresolved blocking contradiction with canonical domain assets or Decisions remains.

Write findings to the Change evidence directory and block implementation on unresolved critical findings.
