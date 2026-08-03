---
name: to-tickets
description: Break an approved OpenSpec Change into dependency-aware tracer-bullet tickets.
disable-model-invocation: true
---

# To Tickets

1. Require an approved Proposal, Specs and Design.
2. Break work into narrow vertical slices that each produce independently demonstrable behavior across the necessary layers.
3. Size every Ticket for one fresh Agent context window.
4. Put prefactoring first only when it makes a later change materially safer.
5. Declare blocking edges and keep the executable frontier explicit.
6. Write the human plan to `tasks.md` and the machine-readable graph to `implementation/tracer-tickets.yaml`.
7. Each Ticket must reference Spec IDs and acceptance criteria, but avoid fragile file paths.
8. GitHub Issues may mirror the Tickets; the Change remains the source of truth.
