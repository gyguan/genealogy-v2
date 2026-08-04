---
name: openspec-validation
description: Validate an OpenSpec Change for completeness, consistency, testability, gate readiness and traceability.
---

# OpenSpec Validation

Check that:

- goal, non-goals, Change type, applicable Capability IDs, affected domains and Decision IDs are explicit and valid;
- each requirement has a stable ID and observable acceptance scenario;
- each Spec file is named after an affected domain or the approved cross-cutting scope;
- Design addresses domain, data, module boundary, privacy, failure and migration impact;
- each Task traces to existing Spec IDs and declares tests and Evidence;
- tests use a stable public Seam;
- Change status is consistent with its Gate approvals;
- no unresolved blocking contradiction with canonical domain assets or Accepted Decisions remains.

Write findings to the Change evidence directory, run `python tools/validate_repo.py`, and block implementation on unresolved critical findings.
