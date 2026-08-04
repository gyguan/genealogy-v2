#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
DOMAIN_STATES = {"draft", "review", "approved", "deprecated"}
CHANGE_TYPES = {"product", "domain", "engineering", "governance", "security"}
CHANGE_STATES = {"draft", "review", "approved", "implementing", "completed", "cancelled"}
GATE_STATES = {"blocked", "pending", "approved", "rejected"}
TASK_STATES = {"planned", "ready", "in-progress", "completed", "blocked", "cancelled"}
DECISION_STATES = {"proposed", "accepted", "rejected", "superseded", "deprecated"}
DEPENDENCY_TYPES = {"identity-reference", "fact-reference", "command-orchestration", "evidence-validation", "snapshot-source", "event-subscription"}


def fail(message: str) -> None:
    ERRORS.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{rel(path)}: invalid YAML: {exc}")
        return None


def meta(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"{rel(path)}: missing YAML frontmatter")
        return None
    try:
        value = yaml.safe_load(text[4:].split("\n---\n", 1)[0])
    except Exception as exc:
        fail(f"{rel(path)}: invalid frontmatter: {exc}")
        return None
    if not isinstance(value, dict):
        fail(f"{rel(path)}: frontmatter must be an object")
        return None
    return value


def sections(path: Path, required: list[str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for title in required:
        if f"## {title}" not in text:
            fail(f"{rel(path)}: missing section ## {title}")


def domain_ids() -> set[str]:
    data = load(ROOT / "domains/context-map.yaml") or {}
    contexts = data.get("contexts", []) if isinstance(data, dict) else []
    ids, graph = set(), {}
    if not isinstance(contexts, list):
        fail("domains/context-map.yaml: contexts must be a list")
        return ids
    for context in contexts:
        if not isinstance(context, dict) or not isinstance(context.get("id"), str):
            fail("domains/context-map.yaml: every context needs an id")
            continue
        current = context["id"]
        if current in ids:
            fail(f"domains/context-map.yaml: duplicate context id {current}")
        ids.add(current)
        graph[current] = []
        deps = context.get("dependencies", [])
        if not isinstance(deps, list):
            fail(f"domains/context-map.yaml: {current}.dependencies must be a list")
            continue
        seen = set()
        for dep in deps:
            target = dep.get("target") if isinstance(dep, dict) else None
            kind = dep.get("type") if isinstance(dep, dict) else None
            if not isinstance(target, str) or kind not in DEPENDENCY_TYPES:
                fail(f"domains/context-map.yaml: {current} dependency needs valid target and type")
                continue
            if target == current:
                fail(f"domains/context-map.yaml: {current} cannot depend on itself")
            if (target, kind) in seen:
                fail(f"domains/context-map.yaml: duplicate dependency {current}->{target} ({kind})")
            seen.add((target, kind))
            graph[current].append(target)
    for current, targets in graph.items():
        for target in targets:
            if target not in ids:
                fail(f"domains/context-map.yaml: {current} depends on unknown domain {target}")

    visiting, visited = set(), set()
    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            fail("domains/context-map.yaml: dependency cycle " + " -> ".join(trail + [node]))
            return
        if node in visited or node not in graph:
            return
        visiting.add(node)
        for target in graph[node]:
            visit(target, trail + [node])
        visiting.remove(node)
        visited.add(node)
    for current in sorted(ids):
        visit(current, [])

    for current in ids:
        path = ROOT / f"domains/{current}.md"
        if not path.exists():
            fail(f"domains/context-map.yaml: missing domains/{current}.md")
            continue
        fm = meta(path)
        if not fm:
            continue
        if fm.get("id") != current or fm.get("status") not in DOMAIN_STATES:
            fail(f"{rel(path)}: invalid id or status")
        if "depends_on" in fm or "dependencies" in fm:
            fail(f"{rel(path)}: domain dependencies belong only in domains/context-map.yaml")
        sections(path, ["职责", "非职责", "关键不变量", "主要用例"])
    for path in (ROOT / "domains").glob("*.md"):
        if path.name != "README.md":
            fm = meta(path)
            if fm and fm.get("id") not in ids:
                fail(f"{rel(path)}: absent from context-map.yaml")
    return ids


def capabilities(domains: set[str]) -> set[str]:
    data = load(ROOT / "product/capability-map.yaml") or {}
    groups = data.get("capability_groups", []) if isinstance(data, dict) else []
    ids, group_ids = set(), set()
    if not isinstance(groups, list):
        fail("product/capability-map.yaml: capability_groups must be a list")
        return ids
    for group in groups:
        group_id = group.get("id") if isinstance(group, dict) else None
        if not isinstance(group_id, str) or not group_id.startswith("CAP-GROUP-") or group_id in group_ids:
            fail(f"product/capability-map.yaml: invalid or duplicate group id {group_id}")
        group_ids.add(group_id)
        items = group.get("capabilities", []) if isinstance(group, dict) else []
        if not isinstance(items, list):
            fail(f"product/capability-map.yaml: {group_id}.capabilities must be a list")
            continue
        for item in items:
            item_id = item.get("id") if isinstance(item, dict) else None
            if not isinstance(item_id, str) or not re.fullmatch(r"CAP-[A-Z0-9-]+", item_id) or item_id in ids:
                fail(f"product/capability-map.yaml: invalid or duplicate capability id {item_id}")
            ids.add(item_id)
            if item.get("priority") not in {"P0", "P1", "P2"} or item.get("domain") not in domains:
                fail(f"product/capability-map.yaml: {item_id} has invalid priority or domain")
            if not isinstance(item.get("name"), str) or not item["name"].strip():
                fail(f"product/capability-map.yaml: {item_id} needs name")
    return ids


def glossary(domains: set[str]) -> None:
    data = load(ROOT / "domains/glossary.yaml") or {}
    terms = data.get("terms", []) if isinstance(data, dict) else []
    ids, names = set(), set()
    if not isinstance(terms, list):
        fail("domains/glossary.yaml: terms must be a list")
        return
    for term in terms:
        term_id = term.get("id") if isinstance(term, dict) else None
        name = term.get("term") if isinstance(term, dict) else None
        if not isinstance(term_id, str) or not term_id.startswith("TERM-") or term_id in ids:
            fail(f"domains/glossary.yaml: invalid or duplicate term id {term_id}")
        ids.add(term_id)
        if not isinstance(name, str) or not name.strip() or name in names:
            fail(f"domains/glossary.yaml: invalid or duplicate canonical term {name}")
        names.add(name)
        if not isinstance(term.get("definition"), str) or not term["definition"].strip() or term.get("domain") not in domains:
            fail(f"domains/glossary.yaml: {term_id} needs definition and valid domain")
        if not isinstance(term.get("aliases", []), list):
            fail(f"domains/glossary.yaml: {term_id}.aliases must be a list")


def decisions(domains: set[str]):
    ids, data = set(), {}
    for path in sorted((ROOT / "decisions").glob("DEC-*.md")):
        fm = meta(path)
        if not fm:
            continue
        decision_id = fm.get("id")
        if not isinstance(decision_id, str) or not re.fullmatch(r"DEC-\d{4}", decision_id) or decision_id in ids:
            fail(f"{rel(path)}: invalid or duplicate decision id")
            continue
        ids.add(decision_id)
        data[decision_id] = fm
        if not path.name.startswith(decision_id + "-") or fm.get("status") not in DECISION_STATES:
            fail(f"{rel(path)}: invalid filename or status")
        if fm.get("type") not in {"product", "domain", "architecture", "compliance"}:
            fail(f"{rel(path)}: invalid decision type")
        affected = fm.get("affected_domains", [])
        if not isinstance(affected, list) or any(value not in domains for value in affected):
            fail(f"{rel(path)}: invalid affected_domains")
        if not isinstance(fm.get("introduced_by"), str) or not re.fullmatch(r"CHG-\d{4}", fm["introduced_by"]):
            fail(f"{rel(path)}: introduced_by must be a Change id")
        if not isinstance(fm.get("supersedes", []), list):
            fail(f"{rel(path)}: supersedes must be a list")
        if fm.get("status") == "accepted" and not fm.get("effective_at"):
            fail(f"{rel(path)}: accepted decision needs effective_at")
        sections(path, ["背景", "决策", "原因", "备选方案", "影响", "迁移与回退", "关联 Change"])
    for decision_id, fm in data.items():
        for old in fm.get("supersedes", []):
            if old not in ids or data[old].get("superseded_by") != decision_id:
                fail(f"{decision_id}: invalid supersedes link {old}")
        new = fm.get("superseded_by")
        if new is not None and (new not in ids or decision_id not in data[new].get("supersedes", [])):
            fail(f"{decision_id}: invalid superseded_by link {new}")
    return ids, data


def gate(change: Path, name: str, value) -> str | None:
    if not isinstance(value, dict) or value.get("status") not in GATE_STATES:
        fail(f"{rel(change)}/change.yaml: gate {name} must have a valid status")
        return None
    state = value["status"]
    if state == "approved":
        for field in ("approved_by", "approved_at", "evidence"):
            if not value.get(field):
                fail(f"{rel(change)}/change.yaml: approved gate {name} needs {field}")
        evidence = value.get("evidence")
        if isinstance(evidence, str) and not (change / evidence).is_file():
            fail(f"{rel(change)}/change.yaml: gate {name} evidence does not exist: {evidence}")
    return state


def task_blocks(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^##\s+(TASK-[A-Z0-9-]+)(?:\s+.*)?$", text, re.M))
    result = []
    for index, match in enumerate(matches):
        block = text[match.end(): matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        item = {"id": match.group(1)}
        for label, key in (("Specs", "specs"), ("Status", "status"), ("Tests", "tests"), ("Evidence", "evidence")):
            found = re.search(rf"^- {label}:\s*(.+?)\s*$", block, re.M)
            if found:
                item[key] = found.group(1).strip()
        result.append(item)
    return result


def change(path: Path, template: bool, domains: set[str], caps: set[str], decs: set[str], seen: set[str]) -> None:
    for name in ("change.yaml", "proposal.md", "specs", "design.md", "tasks.md", "evidence"):
        if not (path / name).exists():
            fail(f"{rel(path)}: missing {name}")
    data = load(path / "change.yaml") if (path / "change.yaml").exists() else None
    if template or not isinstance(data, dict):
        return
    change_id, kind, state = data.get("id"), data.get("change_type"), data.get("status")
    if not isinstance(change_id, str) or not re.fullmatch(r"CHG-\d{4}", change_id) or change_id in seen:
        fail(f"{rel(path)}/change.yaml: invalid or duplicate change id")
        return
    seen.add(change_id)
    if not path.name.startswith(change_id + "-") or kind not in CHANGE_TYPES or state not in CHANGE_STATES:
        fail(f"{rel(path)}/change.yaml: invalid directory, change_type or status")
        return

    values = {}
    for field, known in (("capabilities", caps), ("affected_domains", domains), ("affected_decisions", decs)):
        items = data.get(field, [])
        if not isinstance(items, list):
            fail(f"{rel(path)}/change.yaml: {field} must be a list")
            items = []
        values[field] = items
        for item in items:
            if item not in known:
                fail(f"{rel(path)}/change.yaml: unknown {field} value {item}")

    gates = data.get("gates") if isinstance(data.get("gates"), dict) else {}
    if not gates:
        fail(f"{rel(path)}/change.yaml: gates must be an object")
    gate_states = {name: gate(path, name, gates.get(name)) for name in ("spec_review", "implementation_approval", "release_approval")}

    scope = {"product": {"product"}, "engineering": {"engineering"}, "governance": {"repository-governance"}, "security": {"security"}, "domain": set()}.get(kind, set())
    spec_files = [p for p in (path / "specs").glob("*.md") if p.name != "README.md"]
    spec_ids = set()
    for spec_file in spec_files:
        if spec_file.stem not in values["affected_domains"] and spec_file.stem not in scope:
            fail(f"{rel(spec_file)}: invalid Spec scope")
        ids = re.findall(r"^##\s+(SPEC-[A-Z0-9-]+)(?:\s|$)", spec_file.read_text(encoding="utf-8"), re.M)
        if not ids:
            fail(f"{rel(spec_file)}: no SPEC id found")
        for spec_id in ids:
            if spec_id in spec_ids:
                fail(f"{rel(path)}: duplicate Spec id {spec_id}")
            spec_ids.add(spec_id)

    tasks, task_ids = task_blocks(path / "tasks.md"), set()
    for item in tasks:
        task_id = item["id"]
        if task_id in task_ids:
            fail(f"{rel(path)}: duplicate Task id {task_id}")
        task_ids.add(task_id)
        if item.get("status") not in TASK_STATES:
            fail(f"{rel(path)}/tasks.md: {task_id} invalid or missing status")
        references = [value.strip() for value in item.get("specs", "").split(",") if value.strip()]
        if not references:
            fail(f"{rel(path)}/tasks.md: {task_id} needs Specs")
        for spec_id in references:
            if spec_id not in spec_ids:
                fail(f"{rel(path)}/tasks.md: {task_id} references unknown Spec {spec_id}")
        if not item.get("tests"):
            fail(f"{rel(path)}/tasks.md: {task_id} needs Tests")
        evidence = item.get("evidence")
        if item.get("status") == "completed" and (not evidence or not (path / evidence).is_file()):
            fail(f"{rel(path)}/tasks.md: {task_id} evidence does not exist: {evidence}")

    sections(path / "proposal.md", ["背景与问题", "关联产品能力", "目标", "非目标", "范围与影响领域", "关联 Decision", "风险", "成功标准"])
    sections(path / "design.md", ["方案概览", "领域与数据影响", "接口与模块边界", "安全与隐私", "测试 Seam", "失败、补偿与回滚", "迁移方案", "备选方案与权衡"])
    if state in {"review", "approved", "implementing", "completed"}:
        if kind in {"product", "domain"} and (not values["capabilities"] or not values["affected_domains"]):
            fail(f"{rel(path)}/change.yaml: {state} {kind} change needs capabilities and affected_domains")
        if not spec_files:
            fail(f"{rel(path)}: {state} change needs real Spec files")
    if state in {"approved", "implementing", "completed"} and gate_states.get("spec_review") != "approved":
        fail(f"{rel(path)}/change.yaml: {state} requires approved spec_review")
    if state in {"approved", "implementing", "completed"} and not tasks:
        fail(f"{rel(path)}: {state} change needs Tasks")
    if state in {"implementing", "completed"} and gate_states.get("implementation_approval") != "approved":
        fail(f"{rel(path)}/change.yaml: {state} requires approved implementation_approval")
    if state == "completed":
        if gate_states.get("release_approval") != "approved":
            fail(f"{rel(path)}/change.yaml: completed requires approved release_approval")
        if any(item.get("status") != "completed" for item in tasks):
            fail(f"{rel(path)}: completed change has unfinished Tasks")
    if state == "cancelled" and not data.get("cancellation_reason"):
        fail(f"{rel(path)}/change.yaml: cancelled change needs cancellation_reason")


def skills() -> None:
    names = set()
    for directory in sorted((ROOT / "skills").iterdir()):
        if not directory.is_dir() or directory.name == "upstream":
            continue
        path = directory / "SKILL.md"
        if not path.exists():
            fail(f"{rel(directory)}: missing SKILL.md")
            continue
        fm = meta(path)
        if not fm:
            continue
        name = fm.get("name")
        if name != directory.name or name in names or not isinstance(fm.get("description"), str):
            fail(f"{rel(path)}: invalid name, duplicate name or missing description")
        names.add(name)


def main() -> int:
    required = ["README.md", "AGENTS.md", "SECURITY.md", "product/README.md", "product/capability-map.yaml", "product/roadmap.md", "domains/README.md", "domains/glossary.yaml", "domains/context-map.yaml", "changes/README.md", "changes/_template/change.yaml", "decisions/README.md", "decisions/_template.md", "skills/README.md", "tools/validate_repo.py"]
    for name in required:
        if not (ROOT / name).exists():
            fail(f"missing required file: {name}")
    for name in ("ai", "knowledge", "changes/active", "changes/archived"):
        if (ROOT / name).exists():
            fail(f"obsolete path must be removed: {name}")

    domains = domain_ids()
    glossary(domains)
    caps = capabilities(domains)
    dec_ids, dec_data = decisions(domains)
    skills()
    change(ROOT / "changes/_template", True, domains, caps, dec_ids, set())
    change_ids: set[str] = set()
    for path in sorted((ROOT / "changes").iterdir()):
        if path.is_dir() and path.name != "_template":
            change(path, False, domains, caps, dec_ids, change_ids)
    for decision_id, fm in dec_data.items():
        if fm.get("introduced_by") not in change_ids | {"CHG-0000"}:
            fail(f"{decision_id}: introduced_by references missing Change {fm.get('introduced_by')}")

    if ERRORS:
        print("Repository validation failed:")
        for message in ERRORS:
            print(f"- {message}")
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
