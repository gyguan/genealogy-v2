#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

from diagnostics import Reporter

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_STATES = {"review", "approved", "implementing", "completed"}
STRICT_POLICY = "strict"
ACTIONS = {"ADDED", "MODIFIED", "REMOVED", "RENAMED"}
PROPOSAL_SECTIONS = (
    "背景与问题",
    "关联产品能力",
    "目标",
    "非目标",
    "范围与影响领域",
    "关联 Decision",
    "风险",
    "成功标准",
)
DESIGN_SECTIONS = (
    "方案概览",
    "领域与数据影响",
    "接口与模块边界",
    "安全与隐私",
    "测试 Seam",
    "失败、补偿与回滚",
    "迁移方案",
    "备选方案与权衡",
)
PLACEHOLDER_PATTERN = re.compile(r"(?i)(?:\bTBD\b|\bTODO\b|待补充|待完善|稍后补充)")
SPEC_PATTERN = re.compile(r"^#{2,3}\s+(SPEC-[A-Z0-9-]+)(?:\s+.*?)?$", re.M)
SCENARIO_PATTERN = re.compile(r"^####\s+Scenario\s+(SCN-[A-Z0-9-]+)(?:\s+.*?)?$", re.M)
TASK_PATTERN = re.compile(r"^##\s+(TASK-[A-Z0-9-]+)(?:\s+.*?)?$", re.M)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_yaml(path: Path, reporter: Reporter) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        reporter.error("CHG-YAML-001", f"invalid YAML: {exc}", rel(path))
        return {}
    if not isinstance(value, dict):
        reporter.error("CHG-YAML-002", "file must contain a YAML object", rel(path))
        return {}
    return value


def markdown_sections(text: str, level: int = 2) -> dict[str, str]:
    pattern = re.compile(rf"^{'#' * level}\s+(.+?)\s*$", re.M)
    matches = list(pattern.finditer(text))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1).strip()] = text[match.end():end].strip()
    return result


def meaningful(value: str) -> bool:
    value = re.sub(r"<!--.*?-->", "", value, flags=re.S)
    value = re.sub(r"(?m)^#{1,6}\s+", "", value)
    value = re.sub(r"[\s\-*_`>#|]+", "", value)
    return bool(value)


def validate_required_sections(
    path: Path,
    required: tuple[str, ...],
    reporter: Reporter,
    strict: bool,
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        reporter.error("CHG-DOC-001", f"cannot read document: {exc}", rel(path))
        return
    sections = markdown_sections(text)
    for title in required:
        if title not in sections:
            reporter.error("CHG-DOC-002", f"missing section ## {title}", rel(path))
        elif not meaningful(sections[title]):
            reporter.error("CHG-DOC-003", f"section ## {title} has no meaningful content", rel(path))
        elif strict and PLACEHOLDER_PATTERN.search(sections[title]):
            reporter.error("CHG-DOC-004", f"section ## {title} contains placeholder content", rel(path))


def split_blocks(pattern: re.Pattern[str], text: str) -> list[tuple[re.Match[str], str]]:
    matches = list(pattern.finditer(text))
    result: list[tuple[re.Match[str], str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match, text[match.end():end]))
    return result


def parse_specs(path: Path, reporter: Reporter, strict: bool) -> tuple[set[str], set[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        reporter.error("SPEC-READ-001", f"cannot read Spec: {exc}", rel(path))
        return set(), set()

    action_sections = {
        title: body for title, body in markdown_sections(text).items() if title in ACTIONS
    }
    if strict and not action_sections:
        reporter.error(
            "SPEC-FORMAT-001",
            "strict Spec needs at least one ## ADDED/MODIFIED/REMOVED/RENAMED section",
            rel(path),
        )

    spec_ids: set[str] = set()
    scenario_ids: set[str] = set()
    for match, block in split_blocks(SPEC_PATTERN, text):
        spec_id = match.group(1)
        if spec_id in spec_ids:
            reporter.error("SPEC-ID-001", f"duplicate Spec id {spec_id}", rel(path))
        spec_ids.add(spec_id)
        if not meaningful(block):
            reporter.error("SPEC-CONTENT-001", f"{spec_id} has no meaningful requirement", rel(path))
        if strict:
            if not re.search(r"^####\s+Requirement\s*$", block, re.M):
                reporter.error("SPEC-FORMAT-002", f"{spec_id} needs #### Requirement", rel(path))
            scenarios = SCENARIO_PATTERN.findall(block)
            if not scenarios:
                reporter.error(
                    "SPEC-SCENARIO-001",
                    f"{spec_id} needs at least one identified #### Scenario SCN-*",
                    rel(path),
                )
            for scenario_id in scenarios:
                if scenario_id in scenario_ids:
                    reporter.error("SPEC-SCENARIO-002", f"duplicate Scenario id {scenario_id}", rel(path))
                scenario_ids.add(scenario_id)
                scenario_match = re.search(
                    rf"^####\s+Scenario\s+{re.escape(scenario_id)}(?:\s+.*?)?$([\s\S]*?)(?=^####\s+Scenario\s+SCN-|^###\s+SPEC-|\Z)",
                    block,
                    re.M,
                )
                scenario_body = scenario_match.group(1) if scenario_match else ""
                for keyword in ("Given", "When", "Then"):
                    if not re.search(rf"^-\s+{keyword}:\s*\S", scenario_body, re.M):
                        reporter.error(
                            "SPEC-SCENARIO-003",
                            f"{scenario_id} needs - {keyword}: with observable content",
                            rel(path),
                        )

    if not spec_ids:
        reporter.error("SPEC-ID-002", "active Change needs at least one Spec requirement", rel(path))
    elif not strict:
        if not action_sections:
            reporter.warning(
                "SPEC-MIGRATION-001",
                "legacy Spec has no explicit ADDED/MODIFIED/REMOVED/RENAMED section",
                rel(path),
            )
        if not SCENARIO_PATTERN.search(text):
            reporter.warning(
                "SPEC-MIGRATION-002",
                "legacy Spec has no machine-traceable Scenario IDs",
                rel(path),
            )
    return spec_ids, scenario_ids


def parse_task_fields(path: Path, reporter: Reporter) -> list[dict[str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        reporter.error("TASK-READ-001", f"cannot read Tasks: {exc}", rel(path))
        return []
    fields = (
        "Specs",
        "Status",
        "Depends on",
        "Tests",
        "Evidence",
        "Scope",
        "Acceptance",
        "Definition of Done",
        "Rollback",
    )
    tasks: list[dict[str, str]] = []
    for match, block in split_blocks(TASK_PATTERN, text):
        item = {"id": match.group(1)}
        for field in fields:
            found = re.search(rf"^-\s+{re.escape(field)}:\s*(.*?)\s*$", block, re.M)
            if found:
                item[field] = found.group(1).strip()
        tasks.append(item)
    return tasks


def csv_values(value: str | None) -> list[str]:
    if not value:
        return []
    if value.lower() in {"none", "n/a", "na", "-", "pending"}:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def load_test_registry(
    change_dir: Path,
    reporter: Reporter,
    strict: bool,
    known_specs: set[str],
) -> dict[str, dict]:
    path = change_dir / "tests.yaml"
    if not path.exists():
        if strict:
            reporter.error("TEST-REGISTRY-001", "strict Change needs tests.yaml", rel(change_dir))
        else:
            reporter.warning("TEST-MIGRATION-001", "legacy Change has no tests.yaml registry", rel(change_dir))
        return {}
    data = load_yaml(path, reporter)
    items = data.get("tests", []) if isinstance(data, dict) else []
    if not isinstance(items, list):
        reporter.error("TEST-REGISTRY-002", "tests must be a list", rel(path))
        return {}
    registry: dict[str, dict] = {}
    for item in items:
        test_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(test_id, str) or not re.fullmatch(r"TEST-[A-Z0-9-]+", test_id):
            reporter.error("TEST-ID-001", f"invalid test id {test_id}", rel(path))
            continue
        if test_id in registry:
            reporter.error("TEST-ID-002", f"duplicate test id {test_id}", rel(path))
            continue
        registry[test_id] = item
        if not isinstance(item.get("command"), str) or not item["command"].strip():
            reporter.error("TEST-COMMAND-001", f"{test_id} needs a command", rel(path))
        specs = item.get("specs", [])
        if not isinstance(specs, list) or not specs:
            reporter.error("TEST-TRACE-001", f"{test_id} needs Specs", rel(path))
        else:
            for spec_id in specs:
                if spec_id not in known_specs:
                    reporter.error("TEST-TRACE-002", f"{test_id} references unknown Spec {spec_id}", rel(path))
    return registry


def validate_traceability(
    change_dir: Path,
    reporter: Reporter,
    strict: bool,
    spec_ids: set[str],
    scenario_ids: set[str],
) -> None:
    tasks_path = change_dir / "tasks.md"
    tasks = parse_task_fields(tasks_path, reporter)
    registry = load_test_registry(change_dir, reporter, strict, spec_ids)
    task_spec_coverage: set[str] = set()
    task_scenario_coverage: set[str] = set()
    test_spec_coverage: set[str] = set()

    for item in registry.values():
        test_spec_coverage.update(value for value in item.get("specs", []) if isinstance(value, str))

    for task in tasks:
        task_id = task["id"]
        status = task.get("Status", "")
        if strict:
            for field in ("Specs", "Status", "Tests", "Scope", "Acceptance", "Definition of Done", "Rollback"):
                if not task.get(field):
                    reporter.error("TASK-FIELD-001", f"{task_id} needs {field}", rel(tasks_path))
        if status == "cancelled":
            continue
        for spec_id in csv_values(task.get("Specs")):
            if spec_id in spec_ids:
                task_spec_coverage.add(spec_id)
        for scenario_id in csv_values(task.get("Acceptance")):
            if scenario_id not in scenario_ids and strict:
                reporter.error(
                    "TASK-TRACE-001",
                    f"{task_id} references unknown Scenario {scenario_id}",
                    rel(tasks_path),
                )
            else:
                task_scenario_coverage.add(scenario_id)
        for test_id in csv_values(task.get("Tests")):
            if test_id not in registry:
                if strict:
                    reporter.error("TASK-TEST-001", f"{task_id} references unknown Test {test_id}", rel(tasks_path))
                else:
                    reporter.warning("TASK-TEST-002", f"{task_id} Test {test_id} is not registered", rel(tasks_path))

    for spec_id in sorted(spec_ids - task_spec_coverage):
        if strict:
            reporter.error("TRACE-SPEC-TASK-001", f"{spec_id} is not covered by a Task", rel(change_dir))
        else:
            reporter.warning("TRACE-SPEC-TASK-002", f"{spec_id} is not covered by a Task", rel(change_dir))
    for spec_id in sorted(spec_ids - test_spec_coverage):
        if strict:
            reporter.error("TRACE-SPEC-TEST-001", f"{spec_id} is not covered by a registered Test", rel(change_dir))
        else:
            reporter.warning("TRACE-SPEC-TEST-002", f"{spec_id} is not covered by a registered Test", rel(change_dir))
    if strict:
        for scenario_id in sorted(scenario_ids - task_scenario_coverage):
            reporter.error("TRACE-SCENARIO-TASK-001", f"{scenario_id} is not accepted by a Task", rel(change_dir))


def validate_change(change_dir: Path, reporter: Reporter) -> None:
    metadata_path = change_dir / "change.yaml"
    if not metadata_path.exists():
        return
    data = load_yaml(metadata_path, reporter)
    state = data.get("status")
    if state not in ACTIVE_STATES:
        return
    strict = data.get("quality_policy") == STRICT_POLICY
    if not strict:
        reporter.warning(
            "CHG-MIGRATION-001",
            "active legacy Change does not use quality_policy: strict; strict rules run as migration warnings",
            rel(metadata_path),
        )

    validate_required_sections(change_dir / "proposal.md", PROPOSAL_SECTIONS, reporter, strict)
    validate_required_sections(change_dir / "design.md", DESIGN_SECTIONS, reporter, strict)

    spec_ids: set[str] = set()
    scenario_ids: set[str] = set()
    specs_dir = change_dir / "specs"
    for path in sorted(specs_dir.glob("*.md")) if specs_dir.exists() else []:
        found_specs, found_scenarios = parse_specs(path, reporter, strict)
        duplicates = spec_ids & found_specs
        for spec_id in sorted(duplicates):
            reporter.error("SPEC-ID-003", f"duplicate Spec id across files: {spec_id}", rel(change_dir))
        spec_ids.update(found_specs)
        scenario_ids.update(found_scenarios)
    validate_traceability(change_dir, reporter, strict, spec_ids, scenario_ids)

    reporter.review(
        "REVIEW-BUSINESS-001",
        "Reviewer must judge whether the requirement and domain semantics are correct; Python does not decide business correctness.",
        rel(change_dir),
    )
    reporter.review(
        "REVIEW-DESIGN-001",
        "Reviewer must judge architecture trade-offs, solution proportionality and risk acceptance.",
        rel(change_dir),
    )
    reporter.review(
        "REVIEW-TEST-001",
        "Reviewer must judge whether scenarios and tests are sufficient for the real risk, even when traceability is complete.",
        rel(change_dir),
    )


def main() -> int:
    reporter = Reporter()
    changes_root = ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
                validate_change(path, reporter)
    print(reporter.render("Change quality validation"))
    return reporter.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
