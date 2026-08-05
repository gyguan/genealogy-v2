#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a YAML object")
    return value


def resolve_change(value: str) -> Path:
    supplied = Path(value)
    if supplied.is_dir():
        return supplied.resolve()
    matches = sorted((ROOT / "changes").glob(f"{value.upper()}-*"))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one Change for {value}, found {len(matches)}")
    return matches[0]


def capability_index() -> dict[str, tuple[str, dict]]:
    manifest = load_yaml(ROOT / "product/capability-map.yaml")
    result: dict[str, tuple[str, dict]] = {}
    for file_name in manifest.get("group_files", []):
        path = ROOT / "product" / str(file_name)
        data = load_yaml(path)
        for item in data.get("group", {}).get("capabilities", []):
            capability_id = item.get("id") if isinstance(item, dict) else None
            if isinstance(capability_id, str):
                result[capability_id] = (str(path.relative_to(ROOT)), item)
    return result


def build_context(change_dir: Path) -> list[str]:
    change = load_yaml(change_dir / "change.yaml")
    cap_index = capability_index()
    paths = [
        "AGENTS.md", "SECURITY.md",
        str((change_dir / "change.yaml").relative_to(ROOT)),
        str((change_dir / "proposal.md").relative_to(ROOT)),
        "product/releases.yaml", "product/capability-map.yaml",
    ]
    design_yaml = change_dir / "design.yaml"
    if design_yaml.is_file():
        paths.append(str(design_yaml.relative_to(ROOT)))
    for capability_id in change.get("capabilities", []):
        record = cap_index.get(capability_id)
        if record is None:
            raise ValueError(f"Unknown capability in Change: {capability_id}")
        paths.append(record[0])
    paths.extend(["domains/context-map.yaml", "domains/glossary.yaml"])
    for domain_id in change.get("affected_domains", []):
        paths.append(f"domains/{domain_id}.md")
    for decision_id in change.get("affected_decisions", []):
        matches = sorted((ROOT / "decisions").glob(f"{decision_id}-*.md"))
        if len(matches) != 1:
            raise ValueError(f"Expected one Decision file for {decision_id}")
        paths.append(str(matches[0].relative_to(ROOT)))
    return list(dict.fromkeys(paths))


def markdown_section(text: str, title: str) -> str:
    match = re.search(rf"^##\s+{re.escape(title)}\s*$", text, re.M)
    if not match:
        return ""
    tail = text[match.end():]
    next_match = re.search(r"^##\s+", tail, re.M)
    return tail[: next_match.start() if next_match else len(tail)].strip()


def bullet_lines(value: str) -> list[str]:
    return [
        match.group(1).strip()
        for line in value.splitlines()
        if (match := re.match(r"^\s*[-*]\s+(.+)$", line))
    ]


def decision_summary(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    status_match = re.search(r"^status:\s*(.+)$", text, re.M)
    decision = markdown_section(text, "Decision") or markdown_section(text, "决策")
    return {
        "id": "-".join(path.name.split("-")[:2]),
        "title": title_match.group(1).strip() if title_match else path.stem,
        "status": status_match.group(1).strip() if status_match else None,
        "decision": decision[:1200],
        "source": str(path.relative_to(ROOT)),
    }


def domain_summary(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    metadata: dict = {}
    if text.startswith("---\n") and "\n---\n" in text[4:]:
        raw, text = text[4:].split("\n---\n", 1)
        value = yaml.safe_load(raw)
        if isinstance(value, dict):
            metadata = value
    return {
        "id": metadata.get("id", path.stem),
        "status": metadata.get("status"),
        "responsibility": markdown_section(text, "职责"),
        "non_responsibility": markdown_section(text, "非职责"),
        "invariants": bullet_lines(markdown_section(text, "关键不变量")),
        "source": str(path.relative_to(ROOT)),
    }


def build_bundle(change_dir: Path) -> dict:
    change = load_yaml(change_dir / "change.yaml")
    cap_index = capability_index()
    capabilities: list[dict] = []
    releases: set[str] = set()
    for capability_id in change.get("capabilities", []):
        record = cap_index.get(capability_id)
        if record is None:
            raise ValueError(f"Unknown capability in Change: {capability_id}")
        source, item = record
        capability = dict(item)
        capability["source"] = source
        capabilities.append(capability)
        target_release = item.get("target_release")
        if isinstance(target_release, str):
            releases.add(target_release)

    domains = [domain_summary(ROOT / "domains" / f"{domain_id}.md") for domain_id in change.get("affected_domains", [])]
    decisions: list[dict] = []
    for decision_id in change.get("affected_decisions", []):
        matches = sorted((ROOT / "decisions").glob(f"{decision_id}-*.md"))
        if len(matches) != 1:
            raise ValueError(f"Expected one Decision file for {decision_id}")
        decisions.append(decision_summary(matches[0]))

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    proposal_path = change_dir / "proposal.md"
    design_path = change_dir / "design.yaml"
    return {
        "change": {
            "id": change.get("id"),
            "title": change.get("title"),
            "type": change.get("change_type"),
            "profile": change.get("change_profile"),
            "status": change.get("status"),
            "issue": change.get("issue"),
        },
        "target_releases": sorted(releases),
        "capabilities": capabilities,
        "domains": domains,
        "decisions": decisions,
        "global_constraints": bullet_lines(markdown_section(agents, "全局红线")),
        "security_constraints": bullet_lines(security),
        "proposal": proposal_path.read_text(encoding="utf-8"),
        "machine_design": load_yaml(design_path) if design_path.is_file() else None,
        "source_paths": build_context(change_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the minimum repository context for a Change")
    parser.add_argument("change", help="Change ID such as CHG-0004, or a Change directory")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--bundle", action="store_true", help="emit a compact AI Context Pack")
    args = parser.parse_args()
    try:
        change_dir = resolve_change(args.change)
        value = build_bundle(change_dir) if args.bundle else build_context(change_dir)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Context resolution failed: {exc}")
        return 1
    if args.bundle and not args.json:
        print(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120))
    elif args.json:
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print("\n".join(value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
