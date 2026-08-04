#!/usr/bin/env python3
from __future__ import annotations

import re
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
ROADMAP_REQUIRED = ("用户目标", "纵向闭环", "主要能力", "明确不包含", "版本验收", "成功指标", "核心风险")
PLACEHOLDERS = {"待补充", "待完善", "tbd", "todo", "n/a", "na", "无"}
BASE_CLOSURE_ROLES = {"source", "review", "readback", "portability", "recovery"}
GOVERNED_RELEASE_STATES = {"planned", "in-progress", "delivered"}
GOVERNED_PLANNING_DEPTHS = {"detailed", "bounded"}


def fail(message: str) -> None:
    ERRORS.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{rel(path)}: invalid YAML: {exc}")
        return None


def domain_ids() -> set[str]:
    data = load_yaml(ROOT / "domains/context-map.yaml") or {}
    contexts = data.get("contexts", []) if isinstance(data, dict) else []
    return {
        item["id"]
        for item in contexts
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def validate_releases() -> tuple[dict[str, dict], dict[str, int], list[str]]:
    path = ROOT / "product/releases.yaml"
    data = load_yaml(path) or {}
    items = data.get("releases", []) if isinstance(data, dict) else []
    records: dict[str, dict] = {}
    order: dict[str, int] = {}
    if not isinstance(items, list) or not items:
        fail("product/releases.yaml: releases must be a non-empty list")
        return records, order, []

    for position, item in enumerate(items):
        release_id = item.get("id") if isinstance(item, dict) else None
        if (
            not isinstance(release_id, str)
            or not re.fullmatch(r"V\d+\.\d+", release_id)
            or release_id in records
        ):
            fail(f"product/releases.yaml: invalid or duplicate release id {release_id}")
            continue
        records[release_id] = item
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
        if item.get("status") == "candidate":
            if item.get("planning_confidence") != "low":
                fail(f"product/releases.yaml: candidate {release_id} must have low planning_confidence")
            if item.get("planning_depth") not in {"outcome-only", "candidate-only"}:
                fail(f"product/releases.yaml: candidate {release_id} has excessive planning depth")

    governed_releases = [
        release_id
        for release_id, item in sorted(records.items(), key=lambda pair: order[pair[0]])
        if item.get("status") in GOVERNED_RELEASE_STATES
        and item.get("planning_depth") in GOVERNED_PLANNING_DEPTHS
    ]
    first_governed = governed_releases[0] if governed_releases else None
    for release_id in governed_releases:
        closure = records[release_id].get("closure")
        required_roles = set(BASE_CLOSURE_ROLES)
        if release_id != first_governed:
            required_roles.add("authorization")
        if not isinstance(closure, dict):
            fail(f"product/releases.yaml: {release_id} needs closure mapping")
            continue
        missing = sorted(required_roles - set(closure))
        if missing:
            fail(f"product/releases.yaml: {release_id} closure missing {', '.join(missing)}")
        for role, capability_id in closure.items():
            if not isinstance(role, str) or not isinstance(capability_id, str) or not capability_id:
                fail(f"product/releases.yaml: {release_id} has invalid closure entry {role}")

    return records, order, governed_releases


def roadmap_sections(block: str) -> dict[str, str]:
    headings = list(re.finditer(r"^###\s+(.+?)\s*$", block, re.M))
    sections: dict[str, str] = {}
    for index, match in enumerate(headings):
        title = match.group(1).strip()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(block)
        if title in sections:
            fail(f"product/roadmap.md: duplicate section ### {title}")
        sections[title] = block[match.end():end].strip()
    return sections


def meaningful(text: str) -> bool:
    normalized = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    normalized = re.sub(r"^[\s\-*]+|[\s\-*]+$", "", normalized).strip().lower()
    return bool(normalized) and normalized not in PLACEHOLDERS


def validate_roadmap(release_data: dict[str, dict], governed_releases: list[str]) -> None:
    path = ROOT / "product/roadmap.md"
    if not path.exists():
        fail("missing required product file: product/roadmap.md")
        return
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^##\s+(V\d+\.\d+)\b.*$", text, re.M))
    blocks: dict[str, str] = {}
    titles: dict[str, str] = {}
    for index, match in enumerate(headings):
        release_id = match.group(1)
        if release_id in blocks:
            fail(f"product/roadmap.md: duplicate release heading {release_id}")
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        blocks[release_id] = text[match.end():end]
        titles[release_id] = match.group(0)

    for release_id in release_data:
        if release_id not in blocks:
            fail(f"product/roadmap.md: missing release {release_id}")
    for release_id in blocks:
        if release_id not in release_data:
            fail(f"product/roadmap.md: unknown release {release_id}")

    for release_id in governed_releases:
        block = blocks.get(release_id)
        if block is None:
            continue
        sections = roadmap_sections(block)
        for title in ROADMAP_REQUIRED:
            if title not in sections:
                fail(f"product/roadmap.md: {release_id} missing exact section ### {title}")
            elif not meaningful(sections[title]):
                fail(f"product/roadmap.md: {release_id} section ### {title} is empty or placeholder")

    for release_id, release in release_data.items():
        if release.get("status") == "candidate" and "候选" not in titles.get(release_id, ""):
            fail(f"product/roadmap.md: {release_id} must be marked as candidate")


def validate_capabilities(
    domains: set[str],
    release_data: dict[str, dict],
    release_order: dict[str, int],
) -> dict[str, dict]:
    manifest_path = ROOT / "product/capability-map.yaml"
    manifest = load_yaml(manifest_path) or {}
    if not isinstance(manifest, dict):
        fail("product/capability-map.yaml: manifest must be an object")
        return {}
    if "capability_groups" in manifest:
        fail("product/capability-map.yaml: hand-maintained compatibility projection is forbidden")
    if manifest.get("release_source") != "releases.yaml":
        fail("product/capability-map.yaml: release_source must be releases.yaml")
    if manifest.get("capability_directory") != "capabilities":
        fail("product/capability-map.yaml: capability_directory must be capabilities")

    files = manifest.get("group_files", [])
    if not isinstance(files, list) or not files:
        fail("product/capability-map.yaml: group_files must be a non-empty list")
        return {}
    if len({str(value) for value in files}) != len(files):
        fail("product/capability-map.yaml: group_files contains duplicates")

    listed = {str(value) for value in files}
    actual = {
        str(path.relative_to(ROOT / "product"))
        for path in (ROOT / "product/capabilities").glob("*.yaml")
    }
    for value in sorted(listed - actual):
        fail(f"product/capability-map.yaml: listed capability file does not exist: {value}")
    for value in sorted(actual - listed):
        fail(f"product/{value}: capability file is not listed in capability-map.yaml")

    capability_ids: set[str] = set()
    group_ids: set[str] = set()
    records: dict[str, dict] = {}
    paths: dict[str, str] = {}
    required_fields = {
        "id",
        "name",
        "description",
        "capability_type",
        "primary_domain",
        "supporting_domains",
        "target_release",
        "release_priority",
        "status",
        "planning_confidence",
        "depends_on",
    }

    for file_name in files:
        path = ROOT / "product" / str(file_name)
        if not path.exists():
            continue
        data = load_yaml(path) or {}
        group = data.get("group") if isinstance(data, dict) else None
        group_id = group.get("id") if isinstance(group, dict) else None
        if (
            not isinstance(group_id, str)
            or not group_id.startswith("CAP-GROUP-")
            or group_id in group_ids
        ):
            fail(f"{rel(path)}: invalid or duplicate group id {group_id}")
            continue
        group_ids.add(group_id)
        if not isinstance(group.get("name"), str) or not group["name"].strip():
            fail(f"{rel(path)}: group {group_id} needs name")
        items = group.get("capabilities", [])
        if not isinstance(items, list) or not items:
            fail(f"{rel(path)}: capabilities must be a non-empty list")
            continue

        for item in items:
            capability_id = item.get("id") if isinstance(item, dict) else None
            if (
                not isinstance(capability_id, str)
                or not re.fullmatch(r"CAP-[A-Z0-9-]+", capability_id)
                or capability_id in capability_ids
            ):
                fail(f"{rel(path)}: invalid or duplicate capability id {capability_id}")
                continue
            capability_ids.add(capability_id)
            records[capability_id] = item
            paths[capability_id] = rel(path)

            missing = sorted(required_fields - set(item))
            if missing:
                fail(f"{rel(path)}: {capability_id} missing fields {', '.join(missing)}")
            if not isinstance(item.get("name"), str) or not item["name"].strip():
                fail(f"{rel(path)}: {capability_id} needs name")
            if not isinstance(item.get("description"), str) or not item["description"].strip():
                fail(f"{rel(path)}: {capability_id} needs description")

            capability_type = item.get("capability_type")
            if capability_type not in CAPABILITY_TYPES:
                fail(f"{rel(path)}: {capability_id} has invalid capability_type")
            if capability_type == "platform" and (
                not isinstance(item.get("platform_area"), str) or not item["platform_area"].strip()
            ):
                fail(f"{rel(path)}: platform capability {capability_id} needs platform_area")

            primary = item.get("primary_domain")
            supporting = item.get("supporting_domains")
            if primary not in domains:
                fail(f"{rel(path)}: {capability_id} has invalid primary_domain {primary}")
            if not isinstance(supporting, list) or any(value not in domains for value in supporting):
                fail(f"{rel(path)}: {capability_id} has invalid supporting_domains")
            elif primary in supporting:
                fail(f"{rel(path)}: {capability_id} repeats primary_domain in supporting_domains")
            elif len(set(supporting)) != len(supporting):
                fail(f"{rel(path)}: {capability_id} has duplicate supporting_domains")

            release_id = item.get("target_release")
            if release_id not in release_data:
                fail(f"{rel(path)}: {capability_id} has unknown target_release {release_id}")
            if item.get("release_priority") not in RELEASE_PRIORITIES:
                fail(f"{rel(path)}: {capability_id} has invalid release_priority")
            if item.get("status") not in CAPABILITY_STATES:
                fail(f"{rel(path)}: {capability_id} has invalid status")
            if item.get("planning_confidence") not in PLANNING_CONFIDENCE:
                fail(f"{rel(path)}: {capability_id} has invalid planning_confidence")
            if release_data.get(release_id, {}).get("status") == "candidate" and (
                item.get("status") != "candidate" or item.get("planning_confidence") != "low"
            ):
                fail(f"{rel(path)}: candidate {capability_id} must have low confidence and candidate status")

            dependencies = item.get("depends_on")
            if not isinstance(dependencies, list) or any(not isinstance(value, str) for value in dependencies):
                fail(f"{rel(path)}: {capability_id}.depends_on must be a list of capability ids")
            elif len(set(dependencies)) != len(dependencies):
                fail(f"{rel(path)}: {capability_id}.depends_on contains duplicates")
            elif capability_id in dependencies:
                fail(f"{rel(path)}: {capability_id} cannot depend on itself")

    graph: dict[str, list[str]] = {}
    for capability_id, item in records.items():
        graph[capability_id] = []
        dependencies = item.get("depends_on", [])
        if not isinstance(dependencies, list):
            continue
        for target in dependencies:
            if target not in records:
                fail(f"{paths[capability_id]}: {capability_id} depends on unknown capability {target}")
                continue
            graph[capability_id].append(target)
            current_release = item.get("target_release")
            target_release = records[target].get("target_release")
            if (
                current_release in release_order
                and target_release in release_order
                and release_order[target_release] > release_order[current_release]
            ):
                fail(
                    f"{paths[capability_id]}: {capability_id} depends on later capability "
                    f"{target} ({target_release})"
                )

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

    return records


def validate_closure(
    release_data: dict[str, dict],
    release_order: dict[str, int],
    records: dict[str, dict],
) -> None:
    for release_id, release in release_data.items():
        closure = release.get("closure")
        if not isinstance(closure, dict):
            continue
        for role, capability_id in closure.items():
            if capability_id not in records:
                fail(
                    f"product/releases.yaml: {release_id} closure {role} references unknown capability "
                    f"{capability_id}"
                )
                continue
            target_release = records[capability_id].get("target_release")
            if (
                release_id in release_order
                and target_release in release_order
                and release_order[target_release] > release_order[release_id]
            ):
                fail(
                    f"product/releases.yaml: {release_id} closure {role} uses later capability "
                    f"{capability_id} ({target_release})"
                )


def main() -> int:
    ERRORS.clear()
    for name in (
        "product/releases.yaml",
        "product/capability-map.yaml",
        "product/capabilities/README.md",
        "product/roadmap.md",
    ):
        if not (ROOT / name).exists():
            fail(f"missing required product file: {name}")

    domains = domain_ids()
    release_data, release_order, governed_releases = validate_releases()
    validate_roadmap(release_data, governed_releases)
    records = validate_capabilities(domains, release_data, release_order)
    validate_closure(release_data, release_order, records)

    if ERRORS:
        print("Product validation failed:")
        for message in ERRORS:
            print(f"- {message}")
        return 1
    print("Product validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
