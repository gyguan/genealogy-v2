#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

DOMAIN_STATES = {"draft", "review", "approved", "deprecated"}
CHANGE_TYPES = {"product", "domain", "engineering", "governance", "security"}
CHANGE_STATES = {"draft", "review", "approved", "implementing", "completed", "cancelled"}
CHANGE_PROFILES = {"lightweight", "standard", "high-risk"}
GATE_STATES = {"blocked", "pending", "approved", "rejected"}
GATE_SOURCES = {"github-issue", "github-pull-request", "github-review", "automated-check"}
TASK_STATES = {"planned", "ready", "in-progress", "completed", "blocked", "cancelled"}
DECISION_STATES = {"proposed", "accepted", "rejected", "superseded", "deprecated"}
DECISION_TYPES = {"product", "domain", "architecture", "compliance"}
DEPENDENCY_TYPES = {
    "identity-reference",
    "fact-reference",
    "command-orchestration",
    "evidence-validation",
    "snapshot-source",
    "event-subscription",
}


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


def frontmatter(path: Path) -> dict | None:
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


def require_sections(path: Path, required: list[str]) -> None:
    if not path.exists():
        return
    headings = {
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+?)\s*$", path.read_text(encoding="utf-8"), re.M)
    }
    for title in required:
        if title not in headings:
            fail(f"{rel(path)}: missing section ## {title}")


def validate_domains() -> set[str]:
    path = ROOT / "domains/context-map.yaml"
    data = load_yaml(path) or {}
    contexts = data.get("contexts", []) if isinstance(data, dict) else []
    ids: set[str] = set()
    graph: dict[str, list[str]] = {}
    if not isinstance(contexts, list):
        fail("domains/context-map.yaml: contexts must be a list")
        return ids

    for context in contexts:
        context_id = context.get("id") if isinstance(context, dict) else None
        if not isinstance(context_id, str) or not context_id or context_id in ids:
            fail(f"domains/context-map.yaml: invalid or duplicate context id {context_id}")
            continue
        ids.add(context_id)
        graph[context_id] = []
        dependencies = context.get("dependencies", [])
        if not isinstance(dependencies, list):
            fail(f"domains/context-map.yaml: {context_id}.dependencies must be a list")
            continue
        seen: set[tuple[str, str]] = set()
        for dependency in dependencies:
            target = dependency.get("target") if isinstance(dependency, dict) else None
            kind = dependency.get("type") if isinstance(dependency, dict) else None
            if not isinstance(target, str) or kind not in DEPENDENCY_TYPES:
                fail(f"domains/context-map.yaml: {context_id} dependency needs valid target and type")
                continue
            if target == context_id:
                fail(f"domains/context-map.yaml: {context_id} cannot depend on itself")
            key = (target, kind)
            if key in seen:
                fail(f"domains/context-map.yaml: duplicate dependency {context_id}->{target} ({kind})")
            seen.add(key)
            graph[context_id].append(target)

    for context_id, targets in graph.items():
        for target in targets:
            if target not in ids:
                fail(f"domains/context-map.yaml: {context_id} depends on unknown domain {target}")

    visiting: set[str] = set()
    visited: set[str] = set()

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

    for context_id in sorted(ids):
        visit(context_id, [])

    for context_id in ids:
        domain_path = ROOT / f"domains/{context_id}.md"
        if not domain_path.exists():
            fail(f"domains/context-map.yaml: missing domains/{context_id}.md")
            continue
        metadata = frontmatter(domain_path)
        if metadata:
            if metadata.get("id") != context_id or metadata.get("status") not in DOMAIN_STATES:
                fail(f"{rel(domain_path)}: invalid id or status")
            if "depends_on" in metadata or "dependencies" in metadata:
                fail(f"{rel(domain_path)}: domain dependencies belong only in domains/context-map.yaml")
        require_sections(domain_path, ["职责", "非职责", "关键不变量", "主要用例"])

    for domain_path in (ROOT / "domains").glob("*.md"):
        if domain_path.name == "README.md":
            continue
        metadata = frontmatter(domain_path)
        if metadata and metadata.get("id") not in ids:
            fail(f"{rel(domain_path)}: absent from domains/context-map.yaml")
    return ids


def validate_capability_ids() -> set[str]:
    manifest_path = ROOT / "product/capability-map.yaml"
    manifest = load_yaml(manifest_path) or {}
    files = manifest.get("group_files", []) if isinstance(manifest, dict) else []
    ids: set[str] = set()
    if not isinstance(files, list) or not files:
        fail("product/capability-map.yaml: group_files must be a non-empty list")
        return ids
    for file_name in files:
        path = ROOT / "product" / str(file_name)
        if not path.is_file():
            fail(f"product/capability-map.yaml: listed capability file does not exist: {file_name}")
            continue
        data = load_yaml(path) or {}
        group = data.get("group") if isinstance(data, dict) else None
        items = group.get("capabilities", []) if isinstance(group, dict) else []
        if not isinstance(items, list):
            fail(f"{rel(path)}: capabilities must be a list")
            continue
        for item in items:
            capability_id = item.get("id") if isinstance(item, dict) else None
            if (
                not isinstance(capability_id, str)
                or not re.fullmatch(r"CAP-[A-Z0-9-]+", capability_id)
                or capability_id in ids
            ):
                fail(f"{rel(path)}: invalid or duplicate capability id {capability_id}")
            else:
                ids.add(capability_id)
    return ids


def validate_glossary(domain_ids: set[str]) -> None:
    path = ROOT / "domains/glossary.yaml"
    data = load_yaml(path) or {}
    terms = data.get("terms", []) if isinstance(data, dict) else []
    ids: set[str] = set()
    names: set[str] = set()
    if not isinstance(terms, list):
        fail("domains/glossary.yaml: terms must be a list")
        return
    for term in terms:
        term_id = term.get("id") if isinstance(term, dict) else None
        name = term.get("term") if isinstance(term, dict) else None
        if not isinstance(term_id, str) or not term_id.startswith("TERM-") or term_id in ids:
            fail(f"domains/glossary.yaml: invalid or duplicate term id {term_id}")
        else:
            ids.add(term_id)
        if not isinstance(name, str) or not name.strip() or name in names:
            fail(f"domains/glossary.yaml: invalid or duplicate canonical term {name}")
        else:
            names.add(name)
        if (
            not isinstance(term, dict)
            or not isinstance(term.get("definition"), str)
            or not term["definition"].strip()
            or term.get("domain") not in domain_ids
        ):
            fail(f"domains/glossary.yaml: {term_id} needs definition and valid domain")
        if not isinstance(term.get("aliases", []), list):
            fail(f"domains/glossary.yaml: {term_id}.aliases must be a list")


def validate_decisions(domain_ids: set[str]) -> tuple[set[str], dict[str, dict]]:
    ids: set[str] = set()
    records: dict[str, dict] = {}
    for path in sorted((ROOT / "decisions").glob("DEC-*.md")):
        metadata = frontmatter(path)
        if not metadata:
            continue
        decision_id = metadata.get("id")
        if (
            not isinstance(decision_id, str)
            or not re.fullmatch(r"DEC-\d{4}", decision_id)
            or decision_id in ids
        ):
            fail(f"{rel(path)}: invalid or duplicate decision id")
            continue
        ids.add(decision_id)
        records[decision_id] = metadata
        if not path.name.startswith(decision_id + "-"):
            fail(f"{rel(path)}: filename must start with {decision_id}-")
        if metadata.get("status") not in DECISION_STATES:
            fail(f"{rel(path)}: invalid decision status")
        if metadata.get("type") not in DECISION_TYPES:
            fail(f"{rel(path)}: invalid decision type")
        affected = metadata.get("affected_domains", [])
        if not isinstance(affected, list) or any(value not in domain_ids for value in affected):
            fail(f"{rel(path)}: invalid affected_domains")
        introduced_by = metadata.get("introduced_by")
        if not isinstance(introduced_by, str) or not re.fullmatch(r"CHG-\d{4}", introduced_by):
            fail(f"{rel(path)}: introduced_by must be a Change id")
        if not isinstance(metadata.get("supersedes", []), list):
            fail(f"{rel(path)}: supersedes must be a list")
        if metadata.get("status") == "accepted" and not metadata.get("effective_at"):
            fail(f"{rel(path)}: accepted decision needs effective_at")
        require_sections(path, ["背景", "决策", "原因", "备选方案", "影响", "迁移与回退", "关联 Change"])

    for decision_id, metadata in records.items():
        for old_id in metadata.get("supersedes", []):
            if old_id not in ids or records[old_id].get("superseded_by") != decision_id:
                fail(f"{decision_id}: invalid supersedes link {old_id}")
        new_id = metadata.get("superseded_by")
        if new_id is not None and (
            new_id not in ids or decision_id not in records[new_id].get("supersedes", [])
        ):
            fail(f"{decision_id}: invalid superseded_by link {new_id}")
    return ids, records


def validate_evidence_path(change_dir: Path, value: str, label: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        fail(f"{rel(change_dir)}: {label} needs an evidence path")
        return False
    evidence_root = (change_dir / "evidence").resolve()
    target = (change_dir / value).resolve()
    try:
        target.relative_to(evidence_root)
    except ValueError:
        fail(f"{rel(change_dir)}: {label} must stay under evidence/: {value}")
        return False
    if not target.is_file():
        fail(f"{rel(change_dir)}: {label} evidence does not exist: {value}")
        return False
    return True


def validate_gate(change_dir: Path, name: str, value, version: int) -> str | None:
    if not isinstance(value, dict) or value.get("status") not in GATE_STATES:
        fail(f"{rel(change_dir)}/change.yaml: gate {name} must have a valid status")
        return None
    state = value["status"]
    if state == "approved":
        fields = ["approved_by", "approved_at", "evidence"]
        if version >= 2:
            fields.extend(["source", "reference"])
        for field in fields:
            if not value.get(field):
                fail(f"{rel(change_dir)}/change.yaml: approved gate {name} needs {field}")
        if version >= 2 and value.get("source") not in GATE_SOURCES:
            fail(f"{rel(change_dir)}/change.yaml: gate {name} has invalid source")
        evidence = value.get("evidence")
        if isinstance(evidence, str):
            validate_evidence_path(change_dir, evidence, f"gate {name}")
    return state


def parse_tasks(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^##\s+(TASK-[A-Z0-9-]+)(?:\s+.*)?$", text, re.M))
    result: list[dict[str, str]] = []
    fields = (
        ("Specs", "specs"),
        ("Status", "status"),
        ("Depends on", "depends_on"),
        ("Tests", "tests"),
        ("Evidence", "evidence"),
    )
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end():end]
        item = {"id": match.group(1)}
        for label, key in fields:
            found = re.search(rf"^- {re.escape(label)}:\s*(.+?)\s*$", block, re.M)
            if found:
                item[key] = found.group(1).strip()
        result.append(item)
    return result


def validate_task_dependencies(change_dir: Path, tasks: list[dict[str, str]]) -> None:
    task_ids = {item["id"] for item in tasks}
    graph: dict[str, list[str]] = {item["id"]: [] for item in tasks}
    for item in tasks:
        value = item.get("depends_on", "none").strip()
        if value.lower() in {"none", "n/a", "na", "-", ""}:
            continue
        for dependency in [part.strip() for part in value.split(",") if part.strip()]:
            if dependency == item["id"]:
                fail(f"{rel(change_dir)}/tasks.md: {item['id']} cannot depend on itself")
            elif dependency not in task_ids:
                fail(f"{rel(change_dir)}/tasks.md: {item['id']} depends on unknown Task {dependency}")
            else:
                graph[item["id"]].append(dependency)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            fail(f"{rel(change_dir)}/tasks.md: dependency cycle " + " -> ".join(trail + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node, [])


def validate_change(
    change_dir: Path,
    domain_ids: set[str],
    capability_ids: set[str],
    decision_ids: set[str],
    seen_change_ids: set[str],
) -> None:
    required_assets = ("change.yaml", "proposal.md", "specs", "design.md", "tasks.md", "evidence")
    for asset in required_assets:
        if not (change_dir / asset).exists():
            fail(f"{rel(change_dir)}: missing {asset}")

    metadata_path = change_dir / "change.yaml"
    if not metadata_path.exists():
        return
    data = load_yaml(metadata_path)
    if not isinstance(data, dict):
        return

    change_id = data.get("id")
    change_type = data.get("change_type")
    state = data.get("status")
    version = data.get("version", 1)
    if not isinstance(version, int) or version not in {1, 2}:
        fail(f"{rel(metadata_path)}: unsupported Change schema version {version}")
        version = 1
    if (
        not isinstance(change_id, str)
        or not re.fullmatch(r"CHG-\d{4}", change_id)
        or change_id in seen_change_ids
    ):
        fail(f"{rel(metadata_path)}: invalid or duplicate change id")
        return
    seen_change_ids.add(change_id)
    if not change_dir.name.startswith(change_id + "-"):
        fail(f"{rel(metadata_path)}: directory name must start with {change_id}-")
    if change_type not in CHANGE_TYPES:
        fail(f"{rel(metadata_path)}: invalid change_type")
        return
    if state not in CHANGE_STATES:
        fail(f"{rel(metadata_path)}: invalid status")
        return

    profile = data.get("change_profile")
    if version >= 2:
        if profile not in CHANGE_PROFILES:
            fail(f"{rel(metadata_path)}: version 2 needs valid change_profile")
        if change_type in {"product", "domain", "security"} and profile != "high-risk":
            fail(f"{rel(metadata_path)}: {change_type} change must use high-risk")
        if change_type == "governance" and profile == "lightweight":
            fail(f"{rel(metadata_path)}: governance change cannot use lightweight")

    values: dict[str, list[str]] = {}
    for field, known_values in (
        ("capabilities", capability_ids),
        ("affected_domains", domain_ids),
        ("affected_decisions", decision_ids),
    ):
        items = data.get(field, [])
        if not isinstance(items, list):
            fail(f"{rel(metadata_path)}: {field} must be a list")
            items = []
        values[field] = items
        for item in items:
            if item not in known_values:
                fail(f"{rel(metadata_path)}: unknown {field} value {item}")

    gates = data.get("gates") if isinstance(data.get("gates"), dict) else {}
    if not gates:
        fail(f"{rel(metadata_path)}: gates must be an object")
    gate_states = {
        name: validate_gate(change_dir, name, gates.get(name), version)
        for name in ("spec_review", "implementation_approval", "release_approval")
    }

    stable_scopes = {
        "product": {"product"},
        "engineering": {"engineering"},
        "governance": {"repository-governance"},
        "security": {"security"},
        "domain": set(),
    }[change_type]
    spec_files: list[Path] = []
    spec_ids: set[str] = set()
    specs_dir = change_dir / "specs"
    if specs_dir.exists():
        for spec_file in sorted(specs_dir.glob("*.md")):
            if spec_file.name == "README.md":
                continue
            spec_files.append(spec_file)
            if spec_file.stem not in values["affected_domains"] and spec_file.stem not in stable_scopes:
                fail(f"{rel(spec_file)}: invalid Spec scope")
            found_ids = re.findall(
                r"^##\s+(SPEC-[A-Z0-9-]+)(?:\s|$)",
                spec_file.read_text(encoding="utf-8"),
                re.M,
            )
            if not found_ids:
                fail(f"{rel(spec_file)}: no SPEC id found")
            for spec_id in found_ids:
                if spec_id in spec_ids:
                    fail(f"{rel(change_dir)}: duplicate Spec id {spec_id}")
                spec_ids.add(spec_id)

    tasks = parse_tasks(change_dir / "tasks.md")
    task_ids: set[str] = set()
    for item in tasks:
        task_id = item["id"]
        if task_id in task_ids:
            fail(f"{rel(change_dir)}: duplicate Task id {task_id}")
        task_ids.add(task_id)
        if item.get("status") not in TASK_STATES:
            fail(f"{rel(change_dir)}/tasks.md: {task_id} invalid or missing status")
        references = [value.strip() for value in item.get("specs", "").split(",") if value.strip()]
        if not references:
            fail(f"{rel(change_dir)}/tasks.md: {task_id} needs Specs")
        for spec_id in references:
            if spec_id not in spec_ids:
                fail(f"{rel(change_dir)}/tasks.md: {task_id} references unknown Spec {spec_id}")
        if not item.get("tests"):
            fail(f"{rel(change_dir)}/tasks.md: {task_id} needs Tests")
        evidence = item.get("evidence")
        if item.get("status") == "completed" and isinstance(evidence, str):
            validate_evidence_path(change_dir, evidence, f"Task {task_id}")
        elif item.get("status") == "completed":
            fail(f"{rel(change_dir)}/tasks.md: {task_id} needs Evidence")
    validate_task_dependencies(change_dir, tasks)

    require_sections(
        change_dir / "proposal.md",
        ["背景与问题", "关联产品能力", "目标", "非目标", "范围与影响领域", "关联 Decision", "风险", "成功标准"],
    )
    require_sections(
        change_dir / "design.md",
        ["方案概览", "领域与数据影响", "接口与模块边界", "安全与隐私", "测试 Seam", "失败、补偿与回滚", "迁移方案", "备选方案与权衡"],
    )

    active_states = {"review", "approved", "implementing", "completed"}
    if state in active_states:
        if change_type in {"product", "domain"} and (
            not values["capabilities"] or not values["affected_domains"]
        ):
            fail(f"{rel(metadata_path)}: {state} {change_type} change needs capabilities and affected_domains")
        if not spec_files:
            fail(f"{rel(change_dir)}: {state} change needs real Spec files")
    if state in {"approved", "implementing", "completed"}:
        if gate_states.get("spec_review") != "approved":
            fail(f"{rel(metadata_path)}: {state} requires approved spec_review")
        if not tasks:
            fail(f"{rel(change_dir)}: {state} change needs Tasks")
    if state in {"implementing", "completed"} and gate_states.get("implementation_approval") != "approved":
        fail(f"{rel(metadata_path)}: {state} requires approved implementation_approval")
    if state == "completed":
        if gate_states.get("release_approval") != "approved":
            fail(f"{rel(metadata_path)}: completed requires approved release_approval")
        if any(item.get("status") != "completed" for item in tasks):
            fail(f"{rel(change_dir)}: completed change has unfinished Tasks")
    if state == "cancelled" and not data.get("cancellation_reason"):
        fail(f"{rel(metadata_path)}: cancelled change needs cancellation_reason")


def validate_skills() -> None:
    skills_root = ROOT / "skills"
    names: set[str] = set()
    for directory in sorted(skills_root.iterdir()):
        if not directory.is_dir() or directory.name == "upstream":
            continue
        path = directory / "SKILL.md"
        if not path.exists():
            fail(f"{rel(directory)}: missing SKILL.md")
            continue
        metadata = frontmatter(path)
        if not metadata:
            continue
        name = metadata.get("name")
        if (
            name != directory.name
            or name in names
            or not isinstance(metadata.get("description"), str)
            or not metadata["description"].strip()
        ):
            fail(f"{rel(path)}: invalid name, duplicate name or missing description")
        else:
            names.add(name)


def main() -> int:
    ERRORS.clear()
    required = [
        "README.md",
        "AGENTS.md",
        "SECURITY.md",
        "product/README.md",
        "product/releases.yaml",
        "product/capability-map.yaml",
        "product/roadmap.md",
        "domains/README.md",
        "domains/glossary.yaml",
        "domains/context-map.yaml",
        "changes/README.md",
        "changes/_template/change.yaml",
        "changes/_template/proposal.md",
        "changes/_template/design.md",
        "changes/_template/tasks.md",
        "changes/_template/specs",
        "changes/_template/evidence",
        "decisions/README.md",
        "decisions/_template.md",
        "skills/README.md",
        "tools/check.py",
        "tools/context.py",
        "tools/new_change.py",
        "tools/validate_repo.py",
        "tools/validate_product.py",
        "tools/validate_pr.py",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(f"missing required file: {name}")

    domain_ids = validate_domains()
    capability_ids = validate_capability_ids()
    validate_glossary(domain_ids)
    decision_ids, decision_records = validate_decisions(domain_ids)

    seen_change_ids: set[str] = set()
    changes_root = ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
                validate_change(path, domain_ids, capability_ids, decision_ids, seen_change_ids)

    for decision_id, metadata in decision_records.items():
        introduced_by = metadata.get("introduced_by")
        if introduced_by not in seen_change_ids:
            fail(f"{decision_id}: introduced_by references unknown Change {introduced_by}")

    validate_skills()

    if ERRORS:
        print("Repository validation failed:")
        for message in ERRORS:
            print(f"- {message}")
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
