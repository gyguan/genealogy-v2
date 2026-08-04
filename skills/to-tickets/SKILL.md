---
name: to-tickets
description: Break an approved OpenSpec into independently implementable and machine-traceable vertical slices.
---
# To Tickets
1. Read approved Spec and Design.
2. Split by observable end-to-end behavior, not technical layers.
3. Use stable TASK headings and exact Specs, Status, Depends on, Tests, Evidence fields.
4. Add vertical scope, acceptance, definition of done and rollback.
5. Prefer the smallest number of independently reviewable slices.
6. Do not add behavior outside Spec.
7. Run `python tools/check.py` before implementation approval.
