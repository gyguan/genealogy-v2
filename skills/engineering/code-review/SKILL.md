---
name: code-review
description: Review a fixed diff independently against repository standards and the approved OpenSpec Change.
---

# Code Review

1. Pin a fixed comparison point and confirm the diff is non-empty.
2. Locate the originating Change through branch, commit, PR or Change ID.
3. Run two independent review axes:
   - Standards: `AGENTS.md`, contribution rules, domain invariants, security/privacy rules and code smells.
   - Spec: missing or partial requirements, wrong behavior and scope creep against approved Specs and acceptance criteria.
4. Keep findings separate so one axis cannot hide the other.
5. Cite files and Spec IDs for every actionable finding.
6. Write the report to `changes/active/<change-id>/reviews/code-review.md`.
7. Blocking findings must be resolved or explicitly accepted at a human gate before completion.
