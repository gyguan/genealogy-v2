#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def capability_index() -> dict[str, str]:
    manifest = load_yaml(ROOT / "product/capability-map.yaml")
    result: dict[str, str] = {}
    for file_name in manifest.get("group_files", []):
        path = ROOT / "product" / str(file_name)
        data = load_yaml(path)
        for item in data.get("group", {}).get("capabilities", []):
            capability_id = item.get("id") if isinstance(item, dict) else None
            if isinstance(capability_id, str):
                result[capability_id] = str(path.relative_to(ROOT))
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
    for capability_id in change.get("capabilities", []):
        file_name = cap_index.get(capability_id)
        if file_name is None:
            raise ValueError(f"Unknown capability in Change: {capability_id}")
        paths.append(file_name)
    paths.extend(["domains/context-map.yaml", "domains/glossary.yaml"])
    for domain_id in change.get("affected_domains", []):
        paths.append(f"domains/{domain_id}.md")
    for decision_id in change.get("affected_decisions", []):
        matches = sorted((ROOT / "decisions").glob(f"{decision_id}-*.md"))
        if len(matches) != 1:
            raise ValueError(f"Expected one Decision file for {decision_id}")
        paths.append(str(matches[0].relative_to(ROOT)))
    return list(dict.fromkeys(paths))


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the minimum repository context for a Change")
    parser.add_argument("change", help="Change ID such as CHG-0004, or a Change directory")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()
    try:
        paths = build_context(resolve_change(args.change))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Context resolution failed: {exc}")
        return 1
    print(json.dumps(paths, ensure_ascii=False, indent=2) if args.json else "\n".join(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
