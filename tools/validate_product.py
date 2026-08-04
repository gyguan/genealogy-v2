#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
RELEASE_STATES = {"candidate", "planned", "in-progress", "delivered", "deprecated"}
PLANNING_DEPTHS = {"detailed", "bounded", "outcome-only", "candidate-only"}
CAPABILITY_TYPES = {"business", "application", "platform"}
CAPABILITY_STATES = {"candidate", "planned", "in-progress", "delivered", "deprecated"}
RELEASE_PRIORITIES = {"must", "should", "could"}
PLANNING_CONFIDENCE = {"high", "medium", "low"}


def fail(message: str) -> None:
    ERRORS.append(message)


def load(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def domain_ids() -> set[str]:
    data = load(ROOT / "domains/context-map.yaml") or {}
    values = data.get("contexts", []) if isinstance(data, dict) else []
    return {
        item["id"]
        for item in values
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def releases() -> tuple[dict[str, dict], dict[str, int]]:
    data = load(ROOT / "product/releases.yaml") or {}
    items = data.get("releases", []) if isinstance(data, dict) else []
    result: dict[str, dict] = {}
    order: dict[str, int] = {}
    if not isinstance(items, list) or not items:
        fail("product/releases.yaml: releases must be a non-empty list")
        return result, order
    for position, item in enumerate(items):
        release_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(release_id, str) or not re.fullmatch(r"V\d+\.\d+", release_id) or release_id in result:
            fail(f"product/releases.yaml: invalid or duplicate release id {release_id}")
            continue
        result[release_id] = item
        order[release_id] = position
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            fail(f"product/releases.yaml: {release_id} needs name")
        if not isinstance(item.get("goal"), str) or not item["goal"].strip():
            fail(f"product/releases.yaml: {release_id} needs goal")
        if item.get("status") not in RELEASE_STATES:
            fail(f"product/releases.yaml: {release_id} has invalid status")
        if item.get("planning_confidence") not in PLANNING_CONFIDENCE:
            fail(f"product/releases.yaml: {release_id} has invalid planning_confidence")
        if item.get("planning_depth") not in PLANNING_DEPTHS:
            fail(f"product/releases.yaml: {release_id} has invalid planning_depth")
        if item.get("status") == "candidate" and item.get("planning_confidence") != "low":
            fail(f"product/releases.yaml: candidate {release_id} must have low planning_confidence")
    return result, order


def roadmap() -> None:
    path = ROOT / "product/roadmap.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    headings = list(re.finditer(r"^##\s+(V\d+\.\d+)\b.*$", text, re.M))
    blocks: dict[str, str] = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        blocks[match.group(1)] = text[match.end():end]
    required = ["用户目标", "纵向闭环", "主要能力", "明确不包含", "版本验收", "成功指标", "核心风险"]
    for release_id in ("V0.1", "V0.2", "V0.3", "V0.4", "V0.5"):
        block = blocks.get(release_id)
        if block is None:
            fail(f"product/roadmap.md: missing release {release_id}")
            continue
        for title in required:
            if f"### {title}" not in block:
                fail(f"product/roadmap.md: {release_id} missing section ### {title}")
    for release_id in ("V1.1", "V1.2", "V2.0"):
        heading = next((m.group(0) for m in headings if m.group(1) == release_id), "")
        if "候选" not in heading:
            fail(f"product/roadmap.md: {release_id} must be marked as candidate")


def capabilities(domains: set[str], release_data: dict[str, dict], release_order: dict[str, int]) -> set[str]:
    manifest_path = ROOT / "product/capability-map.yaml"
    manifest = load(manifest_path) or {}
    files = manifest.get("group_files", []) if isinstance(manifest, dict) else []
    if not isinstance(files, list) or not files:
        fail("product/capability-map.yaml: group_files must be a non-empty list")
        return set()
    listed = {str(value) for value in files}
    actual = {
        str(path.relative_to(ROOT / "product"))
        for path in (ROOT / "product/capabilities").glob("*.yaml")
    }
    for value in sorted(listed - actual):
        fail(f"product/capability-map.yaml: listed capability file does not exist: {value}")
    for value in sorted(actual - listed):
        fail(f"product/{value}: capability file is not listed in capability-map.yaml")

    ids: set[str] = set()
    groups: set[str] = set()
    records: dict[str, dict] = {}
    paths: dict[str, str] = {}
    required = {
        "id", "name", "description", "capability_type", "primary_domain",
        "supporting_domains", "target_release", "release_priority", "status",
        "planning_confidence", "depends_on",
    }
    for file_name in files:
        path = ROOT / "product" / str(file_name)
        if not path.exists():
            continue
        data = load(path) or {}
        group = data.get("group") if isinstance(data, dict) else None
        group_id = group.get("id") if isinstance(group, dict) else None
        if not isinstance(group_id, str) or not group_id.startswith("CAP-GROUP-") or group_id in groups:
            fail(f"{path.relative_to(ROOT)}: invalid or duplicate group id {group_id}")
            continue
        groups.add(group_id)
        items = group.get("capabilities", [])
        if not isinstance(items, list) or not items:
            fail(f"{path.relative_to(ROOT)}: capabilities must be a non-empty list")
            continue
        for item in items:
            item_id = item.get("id") if isinstance(item, dict) else None
            if not isinstance(item_id, str) or not re.fullmatch(r"CAP-[A-Z0-9-]+", item_id) or item_id in ids:
                fail(f"{path.relative_to(ROOT)}: invalid or duplicate capability id {item_id}")
                continue
            ids.add(item_id)
            records[item_id] = item
            paths[item_id] = str(path.relative_to(ROOT))
            missing = sorted(required - set(item))
            if missing:
                fail(f"{path.relative_to(ROOT)}: {item_id} missing fields {', '.join(missing)}")
            if not isinstance(item.get("name"), str) or not item["name"].strip():
                fail(f"{path.relative_to(ROOT)}: {item_id} needs name")
            if not isinstance(item.get("description"), str) or not item["description"].strip():
                fail(f"{path.relative_to(ROOT)}: {item_id} needs description")
            if item.get("capability_type") not in CAPABILITY_TYPES:
                fail(f"{path.relative_to(ROOT)}: {item_id} has invalid capability_type")
            if item.get("capability_type") == "platform" and not isinstance(item.get("platform_area"), str):
                fail(f"{path.relative_to(ROOT)}: platform capability {item_id} needs platform_area")
            primary = item.get("primary_domain")
            supporting = item.get("supporting_domains")
            if primary not in domains:
                fail(f"{path.relative_to(ROOT)}: {item_id} has invalid primary_domain {primary}")
            if not isinstance(supporting, list) or any(value not in domains for value in supporting):
                fail(f"{path.relative_to(ROOT)}: {item_id} has invalid supporting_domains")
            elif primary in supporting:
                fail(f"{path.relative_to(ROOT)}: {item_id} repeats primary_domain in supporting_domains")
            release_id = item.get("target_release")
            if release_id not in release_data:
                fail(f"{path.relative_to(ROOT)}: {item_id} has unknown target_release {release_id}")
            if item.get("release_priority") not in RELEASE_PRIORITIES:
                fail(f"{path.relative_to(ROOT)}: {item_id} has invalid release_priority")
            if item.get("status") not in CAPABILITY_STATES:
                fail(f"{path.relative_to(ROOT)}: {item_id} has invalid status")
            if item.get("planning_confidence") not in PLANNING_CONFIDENCE:
                fail(f"{path.relative_to(ROOT)}: {item_id} has invalid planning_confidence")
            if release_data.get(release_id, {}).get("status") == "candidate":
                if item.get("status") != "candidate" or item.get("planning_confidence") != "low":
                    fail(f"{path.relative_to(ROOT)}: candidate {item_id} must have low confidence and candidate status")
            if not isinstance(item.get("depends_on"), list):
                fail(f"{path.relative_to(ROOT)}: {item_id}.depends_on must be a list")

    graph: dict[str, list[str]] = {}
    for item_id, item in records.items():
        graph[item_id] = []
        for target in item.get("depends_on", []):
            if target not in records:
                fail(f"{paths[item_id]}: {item_id} depends on unknown capability {target}")
                continue
            graph[item_id].append(target)
            current_release = item.get("target_release")
            target_release = records[target].get("target_release")
            if current_release in release_order and target_release in release_order and release_order[target_release] > release_order[current_release]:
                fail(f"{paths[item_id]}: {item_id} depends on later capability {target} ({target_release})")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            fail("product capabilities: dependency cycle " + " -> ".join(trail + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, []):
            visit(target, trail + [node])
        visiting.remove(node)
        visited.add(node)
    for node in sorted(graph):
        visit(node, [])

    projection = manifest.get("capability_groups", []) if isinstance(manifest, dict) else []
    projected_ids = {
        item.get("id")
        for group in projection if isinstance(group, dict)
        for item in group.get("capabilities", []) if isinstance(item, dict)
    }
    if projected_ids != ids:
        fail("product/capability-map.yaml: compatibility projection does not match split capabilities")
    return ids


def main() -> int:
    for name in (
        "product/releases.yaml", "product/capability-map.yaml",
        "product/capabilities/README.md", "product/roadmap.md",
    ):
        if not (ROOT / name).exists():
            fail(f"missing required product file: {name}")
    domains = domain_ids()
    release_data, release_order = releases()
    roadmap()
    capabilities(domains, release_data, release_order)
    if ERRORS:
        print("Product validation failed:")
        for message in ERRORS:
            print(f"- {message}")
        return 1
    print("Product validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
