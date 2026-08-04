---
name: domain-modeling
description: Resolve domain language, boundaries, typed dependencies and invariants and update the canonical domain assets.
---

# Domain Modeling

1. Read `domains/glossary.yaml`, `domains/context-map.yaml` and affected domain files.
2. Distinguish identity, relationship, organization, evidence, project and publication concerns.
3. Add or refine canonical terms, responsibilities, non-responsibilities and invariants.
4. Maintain typed domain dependencies only in `domains/context-map.yaml`; never duplicate them in domain frontmatter.
5. Create a Decision when the choice is long-lived, cross-domain or difficult to reverse.
6. Keep framework, database and file-path details out of domain definitions.
7. Run `python tools/validate_repo.py` to detect unknown targets, duplicate sources and dependency cycles.
