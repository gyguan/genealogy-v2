---
name: grill-with-docs
description: Relentlessly clarify a requirement or design while updating the project glossary, domain assets and decisions.
disable-model-invocation: true
---

# Grill With Docs

Use when a requirement has material ambiguity.

1. Read the current Change if one exists, the affected domain assets and relevant Decisions.
2. Interview around one unresolved branch at a time: actors, facts, states, boundaries, exceptions, privacy and completion.
3. Stress-test answers with concrete Chinese genealogy scenarios and counterexamples.
4. Invoke `domain-modeling` whenever a term, invariant or domain boundary changes.
5. Update `context.yaml` open questions and `proposal.md` as conclusions become stable.
6. Do not decide policy silently, expose assumptions or start implementation.
7. Stop when remaining uncertainty is explicitly recorded and does not block Spec creation.
