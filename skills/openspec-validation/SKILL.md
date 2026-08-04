---
name: openspec-validation
description: Validate an OpenSpec Change for completeness, consistency, testability, gate readiness and traceability.
---
# OpenSpec Validation
Check Change type/Profile, goals/non-goals, Capability/Domain/Decision references, observable requirements, Design risks, Task traceability and stable test seams. Product/domain/security must be high-risk; governance cannot be lightweight. Save findings to Evidence, run `python tools/check.py`, and block unresolved critical findings.
