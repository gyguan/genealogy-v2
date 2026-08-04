---
name: to-tickets
description: Break an approved OpenSpec into independently implementable and verifiable vertical slices.
---

# To Tickets

1. Read the approved Spec and Design.
2. Split work by observable end-to-end behavior, not by frontend, backend or database layer.
3. For each Task record stable ID, Spec IDs, dependencies, implementation scope, acceptance, tests and rollback.
4. Prefer the smallest number of slices that can be implemented and reviewed independently.
5. Do not create Tasks for behavior not present in the approved Spec.
