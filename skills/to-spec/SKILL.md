---
name: to-spec
description: Turn an agreed requirement into an OpenSpec Change without repeating resolved clarification.
---

# To Spec

1. Create `changes/<change-id>/` from `_template/`.
2. Complete `change.yaml` and `proposal.md` using the existing discussion.
3. Select the Change type and link affected Capability IDs when the type is `product` or `domain`; always link affected Domain and Decision IDs when applicable.
4. Write one Spec Delta per affected domain under `specs/`, using the domain ID as the filename. Cross-cutting Change types use their approved stable scope name.
5. Use `ADDED`, `MODIFIED`, `REMOVED` or `RENAMED` sections.
6. Give every requirement a stable `SPEC-...` ID and observable acceptance scenario.
7. Describe the solution, module boundary, test Seam, risks and trade-offs in `design.md`.
8. Do not implement code before the Spec Gate is approved and recorded with evidence.
