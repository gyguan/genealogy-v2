---
name: to-spec
description: Turn an agreed requirement into an OpenSpec Change without repeating resolved clarification.
---

# To Spec

1. Create `changes/<change-id>/` from `_template/`.
2. Complete `change.yaml` and `proposal.md` using the existing discussion.
3. Write one Spec Delta per affected domain under `specs/`.
4. Use `ADDED`, `MODIFIED`, `REMOVED` or `RENAMED` sections.
5. Give every requirement a stable ID and observable acceptance scenario.
6. Describe the solution, test Seam, risks and trade-offs in `design.md`.
7. Do not implement code before the Spec Gate is approved.
