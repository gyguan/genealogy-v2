#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
REQUIRED_FROM_CHANGE_NUMBER = 8
ACTIVE_STATES = {"review", "approved", "implementing", "completed"}
APPROVED_STATES = {"approved", "implementing", "completed"}
DESIGN_STATUSES = {"draft", "review", "approved"}
FACET_STATES = {"required", "not-applicable", "review-required"}
FACETS = (
    "workflow", "domain_model", "state_machine", "persistence", "external_api", "ui",
    "events", "migration", "performance", "security_privacy", "module_consistency", "tests_traceability",
)
SECTIONS = {
    "方案概览", "领域与数据影响", "接口与模块边界", "安全与隐私", "测试 Seam",
    "失败、补偿与回滚", "迁移方案", "备选方案与权衡",
}
KIND_PREFIX = {
    "flow": "FLOW-", "use_case": "UC-", "model": "MODEL-", "rule": "RULE-", "invariant": "INV-",
    "state": "STATE-", "command": "CMD-", "data": "DATA-", "constraint": "CONSTRAINT-",
    "api": "API-", "ui": "UI-", "event": "EVENT-", "migration": "MIG-", "nfr": "NFR-",
    "security": "SEC-", "module": "MODULE-", "failure": "FAIL-", "traceability": "TRACE-",
}
FACET_KINDS = {
    "workflow": {"flow", "use_case"},
    "domain_model": {"model", "rule", "invariant"},
    "state_machine": {"state", "command"},
    "persistence": {"data", "constraint"},
    "external_api": {"api"},
    "ui": {"ui"},
    "events": {"event"},
    "migration": {"migration"},
    "performance": {"nfr"},
    "security_privacy": {"security"},
    "module_consistency": {"module"},
    "tests_traceability": {"traceability"},
}
TEST_REQUIRED_KINDS = {"rule", "invariant", "command", "constraint", "security", "traceability"}
SPEC_REQUIRED_KINDS = {"rule", "invariant", "command", "constraint", "security", "traceability"}
SOURCE_TYPES = {"capability", "domain", "decision", "spec", "security", "issue", "user-confirmed", "repository"}


def fail(message: str) -> None:
    ERRORS.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def is_version_one(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value == 1


def load_yaml(path: Path) -> dict | None:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{rel(path)}: invalid YAML: {exc}")
        return None
    if not isinstance(value, dict):
        fail(f"{rel(path)}: YAML root must be an object")
        return None
    return value


def change_number(value: object) -> int | None:
    match = re.fullmatch(r"CHG-(\d{4})", value) if isinstance(value, str) else None
    return int(match.group(1)) if match else None


def spec_gate_approved(change: dict) -> bool:
    gates = change.get("gates")
    gate = gates.get("spec_review") if isinstance(gates, dict) else None
    return isinstance(gate, dict) and gate.get("status") == "approved"


def expected_status(change: dict) -> str:
    if spec_gate_approved(change) or change.get("status") in APPROVED_STATES:
        return "approved"
    return "review" if change.get("status") == "review" else "draft"


def spec_ids(change_dir: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted((change_dir / "specs").glob("*.md")):
        if path.name != "README.md":
            result.update(re.findall(r"^##\s+(SPEC-[A-Z0-9-]+)(?:\s|$)", path.read_text(encoding="utf-8"), re.M))
    return result


def test_registry(change_dir: Path) -> dict[str, set[str]]:
    path = change_dir / "tests.yaml"
    if not path.is_file():
        fail(f"{rel(change_dir)}: machine design contract requires tests.yaml")
        return {}
    data = load_yaml(path)
    if data is None:
        return {}
    tests = data.get("tests")
    if not isinstance(tests, list):
        fail(f"{rel(path)}: tests must be a list")
        return {}
    result: dict[str, set[str]] = {}
    for item in tests:
        if not isinstance(item, dict):
            continue
        test_id, specs = item.get("id"), item.get("specs")
        if isinstance(test_id, str) and re.fullmatch(r"TEST-[A-Z0-9-]+", test_id):
            result[test_id] = set(specs) if isinstance(specs, list) and all(isinstance(value, str) for value in specs) else set()
    return result


def string_list(value: object, path: Path, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        fail(f"{rel(path)}: {label} must be a string list")
        return []
    if len(value) != len(set(value)):
        fail(f"{rel(path)}: {label} contains duplicates")
    return value


def reference_lists(data: dict, path: Path) -> dict[str, list[str]]:
    refs = data.get("references")
    if not isinstance(refs, dict):
        fail(f"{rel(path)}: references must be an object")
        return {key: [] for key in ("capabilities", "specs", "domains", "decisions")}
    result: dict[str, list[str]] = {}
    for key in ("capabilities", "specs", "domains", "decisions"):
        if key not in refs:
            fail(f"{rel(path)}: references.{key} must be declared explicitly")
            result[key] = []
        else:
            result[key] = string_list(refs[key], path, f"references.{key}")
    return result


def validate_facts(data: dict, path: Path) -> set[str]:
    facts = data.get("facts")
    if not isinstance(facts, list):
        fail(f"{rel(path)}: facts must be a list")
        return set()
    result: set[str] = set()
    for item in facts:
        if not isinstance(item, dict):
            fail(f"{rel(path)}: every fact must be an object")
            continue
        fact_id = item.get("id")
        if not isinstance(fact_id, str) or not re.fullmatch(r"FACT-[A-Z0-9-]+", fact_id):
            fail(f"{rel(path)}: fact id must match FACT-...")
            continue
        if fact_id in result:
            fail(f"{rel(path)}: duplicate fact id {fact_id}")
        result.add(fact_id)
        if not isinstance(item.get("statement"), str) or len(item["statement"].strip()) < 8:
            fail(f"{rel(path)}: fact {fact_id} needs a concrete statement")
        source = item.get("source")
        if not isinstance(source, dict):
            fail(f"{rel(path)}: fact {fact_id} needs a source object")
            continue
        if source.get("type") not in SOURCE_TYPES:
            fail(f"{rel(path)}: fact {fact_id} has unsupported source type")
        if not isinstance(source.get("reference"), str) or len(source["reference"].strip()) < 3:
            fail(f"{rel(path)}: fact {fact_id} needs a source reference")
    return result


def validate_assumptions(data: dict, path: Path, review_ready: bool) -> set[str]:
    assumptions = data.get("assumptions")
    if not isinstance(assumptions, list):
        fail(f"{rel(path)}: assumptions must be a list")
        return set()
    result: set[str] = set()
    for item in assumptions:
        if not isinstance(item, dict):
            fail(f"{rel(path)}: every assumption must be an object")
            continue
        assumption_id = item.get("id")
        if not isinstance(assumption_id, str) or not re.fullmatch(r"ASM-[A-Z0-9-]+", assumption_id):
            fail(f"{rel(path)}: assumption id must match ASM-...")
            continue
        if assumption_id in result:
            fail(f"{rel(path)}: duplicate assumption id {assumption_id}")
        result.add(assumption_id)
        if not isinstance(item.get("statement"), str) or len(item["statement"].strip()) < 8:
            fail(f"{rel(path)}: assumption {assumption_id} needs a concrete statement")
        if item.get("status") not in {"proposed", "confirmed", "rejected"}:
            fail(f"{rel(path)}: assumption {assumption_id} has invalid status")
        if not isinstance(item.get("blocking"), bool):
            fail(f"{rel(path)}: assumption {assumption_id} blocking must be boolean")
        if review_ready and item.get("blocking") and item.get("status") == "proposed":
            fail(f"{rel(path)}: blocking assumption {assumption_id} must be resolved before review")
    return result


def validate_open_questions(data: dict, path: Path, approved: bool) -> set[str]:
    questions = data.get("open_questions")
    if not isinstance(questions, list):
        fail(f"{rel(path)}: open_questions must be a list")
        return set()
    result: set[str] = set()
    for item in questions:
        if not isinstance(item, dict):
            fail(f"{rel(path)}: every open question must be an object")
            continue
        question_id = item.get("id")
        if not isinstance(question_id, str) or not re.fullmatch(r"OPEN-[A-Z0-9-]+", question_id):
            fail(f"{rel(path)}: open question id must match OPEN-...")
            continue
        if question_id in result:
            fail(f"{rel(path)}: duplicate open question id {question_id}")
        result.add(question_id)
        if not isinstance(item.get("question"), str) or len(item["question"].strip()) < 8:
            fail(f"{rel(path)}: open question {question_id} needs concrete text")
        if not isinstance(item.get("owner"), str) or not item["owner"].strip():
            fail(f"{rel(path)}: open question {question_id} needs an owner")
        if not isinstance(item.get("blocking"), bool):
            fail(f"{rel(path)}: open question {question_id} blocking must be boolean")
    if approved and result:
        fail(f"{rel(path)}: approved design cannot contain open questions")
    return result


def validate_definitions(
    data: dict,
    path: Path,
    specs: set[str],
    tests: dict[str, set[str]],
    fact_ids: set[str],
    assumption_ids: set[str],
    decision_ids: set[str],
    review_ready: bool,
) -> dict[str, dict]:
    definitions = data.get("definitions")
    if not isinstance(definitions, list):
        fail(f"{rel(path)}: definitions must be a list")
        return {}
    result: dict[str, dict] = {}
    allowed_basis = fact_ids | assumption_ids | decision_ids | specs
    for item in definitions:
        if not isinstance(item, dict):
            fail(f"{rel(path)}: every definition must be an object")
            continue
        definition_id, kind = item.get("id"), item.get("kind")
        if kind not in KIND_PREFIX:
            fail(f"{rel(path)}: definition {definition_id!r} has invalid kind")
            continue
        prefix = KIND_PREFIX[kind]
        if not isinstance(definition_id, str) or not re.fullmatch(rf"{re.escape(prefix)}[A-Z0-9-]+", definition_id):
            fail(f"{rel(path)}: {kind} definition id must use prefix {prefix}")
            continue
        if definition_id in result:
            fail(f"{rel(path)}: duplicate definition id {definition_id}")
        result[definition_id] = item
        if item.get("section") not in SECTIONS:
            fail(f"{rel(path)}: definition {definition_id} has invalid section")
        if not isinstance(item.get("summary"), str) or len(item["summary"].strip()) < 8:
            fail(f"{rel(path)}: definition {definition_id} needs a concrete summary")
        definition_specs = set(string_list(item.get("specs"), path, f"definition {definition_id}.specs"))
        definition_tests = set(string_list(item.get("tests"), path, f"definition {definition_id}.tests"))
        basis = set(string_list(item.get("basis"), path, f"definition {definition_id}.basis"))
        unknown_specs = sorted(definition_specs - specs)
        unknown_tests = sorted(definition_tests - set(tests))
        unknown_basis = sorted(basis - allowed_basis)
        if unknown_specs:
            fail(f"{rel(path)}: definition {definition_id} references unknown specs: {', '.join(unknown_specs)}")
        if unknown_tests:
            fail(f"{rel(path)}: definition {definition_id} references unknown tests: {', '.join(unknown_tests)}")
        if unknown_basis:
            fail(f"{rel(path)}: definition {definition_id} references unknown basis: {', '.join(unknown_basis)}")
        if review_ready and kind in SPEC_REQUIRED_KINDS and not definition_specs:
            fail(f"{rel(path)}: {kind} definition {definition_id} must link specs")
        if review_ready and kind in TEST_REQUIRED_KINDS and not definition_tests:
            fail(f"{rel(path)}: {kind} definition {definition_id} must link tests")
        if review_ready:
            for test_id in sorted(definition_tests & set(tests)):
                uncovered = sorted(definition_specs - tests[test_id])
                if uncovered:
                    fail(
                        f"{rel(path)}: definition {definition_id} test {test_id} does not cover "
                        f"definition specs: {', '.join(uncovered)}"
                    )
    return result


def validate_facets(data: dict, path: Path, definitions: dict[str, dict], review_ready: bool) -> None:
    facets = data.get("facets")
    if not isinstance(facets, dict):
        fail(f"{rel(path)}: facets must be an object")
        return
    missing, extra = set(FACETS) - set(facets), set(facets) - set(FACETS)
    if missing:
        fail(f"{rel(path)}: missing facets: {', '.join(sorted(missing))}")
    if extra:
        fail(f"{rel(path)}: unknown facets: {', '.join(sorted(extra))}")
    for facet in FACETS:
        value = facets.get(facet)
        if not isinstance(value, dict):
            fail(f"{rel(path)}: facet {facet} must be an object")
            continue
        status, reason = value.get("status"), value.get("reason")
        design_ids = string_list(value.get("design_ids"), path, f"facet {facet}.design_ids")
        if status not in FACET_STATES:
            fail(f"{rel(path)}: facet {facet} has invalid status")
            continue
        if review_ready and status == "review-required":
            fail(f"{rel(path)}: facet {facet} must be resolved before review")
        if status == "required":
            if not isinstance(reason, str) or len(reason.strip()) < 5:
                fail(f"{rel(path)}: required facet {facet} needs a reason")
            if review_ready and not design_ids:
                fail(f"{rel(path)}: required facet {facet} needs design_ids")
            for design_id in design_ids:
                definition = definitions.get(design_id)
                if definition is None:
                    fail(f"{rel(path)}: facet {facet} references unknown definition {design_id}")
                elif definition.get("kind") not in FACET_KINDS[facet]:
                    fail(f"{rel(path)}: facet {facet} references incompatible definition {design_id}")
        elif status == "not-applicable":
            if not isinstance(reason, str) or len(reason.strip()) < 5:
                fail(f"{rel(path)}: not-applicable facet {facet} needs a concrete reason")
            if design_ids:
                fail(f"{rel(path)}: not-applicable facet {facet} cannot list design_ids")
        elif design_ids:
            fail(f"{rel(path)}: review-required facet {facet} cannot list design_ids yet")


def validate_traceability(
    data: dict,
    path: Path,
    specs: set[str],
    definitions: dict[str, dict],
    tests: dict[str, set[str]],
    review_ready: bool,
) -> None:
    traceability = data.get("traceability")
    if not isinstance(traceability, list):
        fail(f"{rel(path)}: traceability must be a list")
        return
    seen: set[str] = set()
    for item in traceability:
        if not isinstance(item, dict):
            fail(f"{rel(path)}: every traceability entry must be an object")
            continue
        spec = item.get("spec")
        if not isinstance(spec, str) or spec not in specs:
            fail(f"{rel(path)}: traceability references unknown spec {spec!r}")
            continue
        if spec in seen:
            fail(f"{rel(path)}: duplicate traceability entry for {spec}")
        seen.add(spec)
        design_ids = set(string_list(item.get("design_ids"), path, f"traceability {spec}.design_ids"))
        test_ids = set(string_list(item.get("tests"), path, f"traceability {spec}.tests"))
        if review_ready and not design_ids:
            fail(f"{rel(path)}: traceability {spec} needs design_ids")
        if review_ready and not test_ids:
            fail(f"{rel(path)}: traceability {spec} needs tests")
        for design_id in sorted(design_ids):
            definition = definitions.get(design_id)
            if definition is None:
                fail(f"{rel(path)}: traceability {spec} references unknown definition {design_id}")
            elif spec not in set(definition.get("specs", [])):
                fail(f"{rel(path)}: definition {design_id} does not declare spec {spec}")
        for test_id in sorted(test_ids):
            if test_id not in tests:
                fail(f"{rel(path)}: traceability {spec} references unknown test {test_id}")
            elif spec not in tests[test_id]:
                fail(f"{rel(path)}: test {test_id} does not cover spec {spec}")
    if review_ready:
        missing = sorted(specs - seen)
        if missing:
            fail(f"{rel(path)}: missing traceability for specs: {', '.join(missing)}")


def validate_template() -> None:
    path = ROOT / "changes/_template/design.yaml"
    if not path.is_file():
        fail("changes/_template/design.yaml: missing machine design template")
        return
    data = load_yaml(path)
    if data is None:
        return
    if not is_version_one(data.get("version")) or data.get("change") != "CHG-0000" or data.get("status") != "draft":
        fail(f"{rel(path)}: template must use integer version 1, CHG-0000 and draft status")
    reference_lists(data, path)
    facts = validate_facts(data, path)
    assumptions = validate_assumptions(data, path, review_ready=False)
    validate_open_questions(data, path, approved=False)
    definitions = validate_definitions(data, path, set(), {}, facts, assumptions, set(), review_ready=False)
    validate_facets(data, path, definitions, review_ready=False)
    if not isinstance(data.get("traceability"), list):
        fail(f"{rel(path)}: traceability must be a list")


def validate_change(change_dir: Path) -> None:
    change_path = change_dir / "change.yaml"
    if not change_path.is_file():
        return
    change = load_yaml(change_path)
    if change is None:
        return
    number, version = change_number(change.get("id")), change.get("design_machine_contract_version")
    if number is not None and number >= REQUIRED_FROM_CHANGE_NUMBER and not is_version_one(version):
        fail(f"{rel(change_path)}: CHG-0008 and later require design_machine_contract_version: integer 1")
        return
    if not is_version_one(version):
        return
    path = change_dir / "design.yaml"
    if not path.is_file():
        fail(f"{rel(change_dir)}: machine design contract requires design.yaml")
        return
    data = load_yaml(path)
    if data is None:
        return
    if not is_version_one(data.get("version")):
        fail(f"{rel(path)}: version must be integer 1")
    if data.get("change") != change.get("id"):
        fail(f"{rel(path)}: change must equal change.yaml id")
    review_ready = change.get("status") in ACTIVE_STATES or spec_gate_approved(change)
    approved = change.get("status") in APPROVED_STATES or spec_gate_approved(change)
    if data.get("status") not in DESIGN_STATUSES:
        fail(f"{rel(path)}: invalid status")
    elif data.get("status") != expected_status(change):
        fail(f"{rel(path)}: status must be {expected_status(change)}")

    refs = reference_lists(data, path)
    expected_refs: dict[str, object] = {
        "capabilities": change.get("capabilities", []),
        "domains": change.get("affected_domains", []),
        "decisions": change.get("affected_decisions", []),
        "specs": sorted(spec_ids(change_dir)),
    }
    for key, expected in expected_refs.items():
        expected_values = expected if isinstance(expected, list) else list(expected)
        if set(refs[key]) != set(expected_values):
            fail(f"{rel(path)}: references.{key} must match formal assets")

    tests = test_registry(change_dir)
    facts = validate_facts(data, path)
    assumptions = validate_assumptions(data, path, review_ready)
    validate_open_questions(data, path, approved)
    definitions = validate_definitions(
        data, path, set(refs["specs"]), tests, facts, assumptions, set(refs["decisions"]), review_ready
    )
    validate_facets(data, path, definitions, review_ready)
    validate_traceability(data, path, set(refs["specs"]), definitions, tests, review_ready)


def main() -> int:
    validate_template()
    for change_dir in sorted((ROOT / "changes").glob("CHG-*")):
        if change_dir.is_dir():
            validate_change(change_dir)
    if ERRORS:
        print("Machine design validation failed:")
        for error in ERRORS:
            print(f"- {error}")
        return 1
    print("Machine design validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
