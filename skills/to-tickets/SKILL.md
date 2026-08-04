---
name: to-tickets
description: Break an approved OpenSpec into independently implementable and machine-traceable vertical slices.
---

# To Tickets

1. Read the approved Spec and Design.
2. Split work by observable end-to-end behavior, not by frontend, backend or database layer.
3. Use a stable `## TASK-...` heading for each Task.
4. Record machine-readable `Specs`, `Status`, `Depends on`, `Tests` and `Evidence` fields exactly as defined by the Change template.
5. Add vertical scope, acceptance, definition of done and rollback sections.
6. Prefer the smallest number of slices that can be implemented and reviewed independently.
7. Do not create Tasks for behavior not present in the approved Spec.
8. Run `python tools/validate_repo.py` before implementation approval.
