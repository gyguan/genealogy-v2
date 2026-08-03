---
name: implement
description: Implement approved OpenSpec tickets, using TDD and producing traceable evidence.
disable-model-invocation: true
---

# Implement

1. Require an approved Change and implementation gate.
2. Select a Ticket whose blockers are complete; do not work around dependency edges.
3. Read only the task context pack, affected domain rules, relevant Decisions and current implementation knowledge.
4. Use `tdd` at the agreed Seams where behavior can be verified.
5. Keep the slice minimal; do not add speculative generality or unrelated cleanup.
6. Run type checking, focused tests and required static checks throughout implementation.
7. Update task-to-code-to-test traceability and store execution evidence.
8. After the Ticket frontier is complete, run the full relevant suite and invoke `code-review`.
9. Do not mark complete while blocking review findings or unmet acceptance criteria remain.
