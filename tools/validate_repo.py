#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def error(message: str) -> None:
    ERRORS.append(message)


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        error(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def markdown_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        error(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return None
    raw = text[4:].split("\n---\n", 1)[0]
    try:
        return yaml.safe_load(raw)
    except Exception as exc:
        error(f"{path.relative_to(ROOT)}: invalid frontmatter: {exc}")
        return None


def validate_change(path: Path, template: bool = False) -> None:
    required = ["change.yaml", "proposal.md", "specs", "design.md", "tasks.md", "evidence"]
    for item in required:
        if not (path / item).exists():
            error(f"{path.relative_to(ROOT)}: missing {item}")

    data = load_yaml(path / "change.yaml") if (path / "change.yaml").exists() else None
    if template or not isinstance(data, dict):
        return
    change_id = data.get("id")
    if not isinstance(change_id, str) or not path.name.startswith(change_id + "-"):
        error(f"{path.relative_to(ROOT)}: directory must start with change id")
    if data.get("status") not in {"draft", "review", "approved", "implementing", "completed", "cancelled"}:
        error(f"{path.relative_to(ROOT)}/change.yaml: invalid status")


def main() -> int:
    required_files = [
        "AGENTS.md",
        "product/README.md",
        "product/capability-map.yaml",
        "product/roadmap.md",
        "domains/glossary.yaml",
        "domains/context-map.yaml",
        "changes/_template/change.yaml",
        "skills/README.md",
        "tools/validate_repo.py",
    ]
    for item in required_files:
        if not (ROOT / item).exists():
            error(f"missing required file: {item}")

    forbidden = ["ai", "docs", "knowledge", "evals", "schemas", "reference", "changes/active", "changes/archived"]
    for item in forbidden:
        if (ROOT / item).exists():
            error(f"obsolete path must be removed: {item}")

    context_map = load_yaml(ROOT / "domains" / "context-map.yaml") or {}
    contexts = context_map.get("contexts", []) if isinstance(context_map, dict) else []
    context_ids: set[str] = set()
    for context in contexts:
        if not isinstance(context, dict) or not isinstance(context.get("id"), str):
            error("domains/context-map.yaml: every context needs an id")
            continue
        context_id = context["id"]
        context_ids.add(context_id)
        domain_file = ROOT / "domains" / f"{context_id}.md"
        if not domain_file.exists():
            error(f"domains/context-map.yaml: missing domains/{context_id}.md")
            continue
        meta = markdown_frontmatter(domain_file)
        if isinstance(meta, dict) and meta.get("id") != context_id:
            error(f"{domain_file.relative_to(ROOT)}: id must match context map")

    for domain_file in (ROOT / "domains").glob("*.md"):
        if domain_file.name == "README.md":
            continue
        meta = markdown_frontmatter(domain_file)
        if isinstance(meta, dict) and meta.get("id") not in context_ids:
            error(f"{domain_file.relative_to(ROOT)}: absent from context-map.yaml")

    names: set[str] = set()
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == "upstream":
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            error(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
            continue
        meta = markdown_frontmatter(skill_file)
        if not isinstance(meta, dict):
            continue
        name = meta.get("name")
        if name != skill_dir.name:
            error(f"{skill_file.relative_to(ROOT)}: name must match directory")
        if name in names:
            error(f"duplicate skill name: {name}")
        names.add(name)

    validate_change(ROOT / "changes" / "_template", template=True)
    for path in sorted((ROOT / "changes").iterdir()):
        if path.is_dir() and path.name != "_template":
            validate_change(path)

    load_yaml(ROOT / "product" / "capability-map.yaml")
    load_yaml(ROOT / "domains" / "glossary.yaml")

    if ERRORS:
        print("Repository validation failed:")
        for item in ERRORS:
            print(f"- {item}")
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
