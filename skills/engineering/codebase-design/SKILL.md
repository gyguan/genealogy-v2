---
name: codebase-design
description: Design deep modules with small interfaces, clean seams, locality and testability.
---

# Codebase Design

Use the vocabulary: Module, Interface, Implementation, Seam, Adapter, Depth, Leverage and Locality.

1. Place a small Interface at a meaningful Seam and hide substantial behavior behind it.
2. The Interface includes invariants, ordering, errors, configuration and performance facts callers must know.
3. Test through the same external Seam used by callers.
4. Prefer accepting dependencies and returning results over hidden construction and side effects.
5. Introduce an Adapter Seam only when behavior actually varies; one adapter is usually hypothetical, two make the variation real.
6. Apply the deletion test: if deleting the Module spreads complexity to many callers, it earns its place.
7. Reject pass-through layers, speculative abstractions and interfaces as complex as their implementation.
8. Record hard-to-reverse Seam choices in `decisions/architecture/` and reflect them in the active Change Design.
