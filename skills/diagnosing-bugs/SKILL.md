---
name: diagnosing-bugs
description: Reproduce, isolate and fix a bug with a durable regression test and documented root cause.
---

# Diagnosing Bugs

1. Reproduce the failure at the highest stable public Seam.
2. Minimize the reproduction and distinguish symptom from root cause.
3. Check whether the bug exposes a missing Spec, domain invariant or Decision.
4. Add a failing regression test, implement the smallest safe fix and run relevant regressions.
5. Record the root cause, fix, evidence and any follow-up Change required.
