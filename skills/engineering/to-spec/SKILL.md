---
name: to-spec
description: Turn the current requirement discussion into an OpenSpec Change without repeating the interview.
disable-model-invocation: true
---

# To Spec

1. Identify or create `changes/active/<change-id>/` from `_template/`.
2. Read the conversation, `context.yaml`, product capability, affected domains and Decisions.
3. Write `proposal.md`: problem, outcome, scope, non-goals, risks and affected domains.
4. Write one delta file per affected domain under `specs/`, using ADDED, MODIFIED, REMOVED or RENAMED sections.
5. Record implementation decisions in `design.md` without premature file paths or code snippets.
6. Define the highest practical public test Seam in `implementation/seams.yaml`; prefer existing Seams and keep their number small.
7. Every requirement must have observable acceptance criteria and privacy implications where relevant.
8. Run OpenSpec validation. Do not create Tickets or code until the Spec is approved.
