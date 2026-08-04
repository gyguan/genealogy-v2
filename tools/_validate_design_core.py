#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
REQUIRED_FROM_CHANGE_NUMBER = 6
ACTIVE_STATES = {"review", "approved", "implementing", "completed"}
APPROVED_STATES = {"approved", "implementing", "completed"}
DESIGN_STATUSES = {"draft", "review", "approved"}
APPLICABILITY_VALUES = {"required", "not-applicable"}

REQUIRED_SECTIONS = (
    "方案概览",
    "领域与数据影响",
    "接口与模块边界",
    "安全与隐私",
    "测试 Seam",
    "失败、补偿与回滚",
    "迁移方案",
    "备选方案与权衡",
)

FACETS: dict[str, tuple[str, tuple[str, ...]]] = {
    "workflow": ("方案概览", ("FLOW-", "UC-")),
    "domain_model": ("领域与数据影响", ("MODEL-", "RULE-", "INV-")),
    "state_machine": ("接口与模块边界", ("STATE-", "CMD-")),
    "persistence": ("领域与数据影响", ("DATA-", "CONSTRAINT-")),
    "external_api": ("接口与模块边界", ("API-",)),
    "ui": ("接口与模块边界", ("UI-",)),
    "events": ("接口与模块边界", ("EVENT-",)),
    "migration": ("迁移方案", ("MIG-",)),
    "performance": ("备选方案与权衡", ("NFR-",)),
    "security_privacy": ("安全与隐私", ("SEC-",)),
    "module_consistency": ("接口与模块边界", ("MODULE-",)),
    "tests_traceability": ("测试 Seam", ("TEST-",)),
}


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


def read_design(path: Path) -> tuple[dict | None, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"{rel(path)}: missing YAML frontmatter")
        return None, text
    raw, body = text[4:].split("\n---\n", 1)
    try:
        metadata = yaml.safe_load(raw)
    except Exception as exc:
        fail(f"{rel(path)}: invalid frontmatter: {exc}")
        return None, body
    if not isinstance(metadata, dict):
        fail(f"{rel(path)}: frontmatter must be an object")
        return None, body
    return metadata, body


def indent_width(value: str) -> int:
    width = 0
    for char in value:
        if char == " ":
            width += 1
        elif char == "\t":
            width += 4 - (width % 4)
        else:
            break
    return width


def visible_markdown(text: str) -> str:
    """Return rendered Markdown while excluding code and raw HTML code blocks."""
    visible: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    fence_indent_limit = 3
    in_indented_code = False
    indented_code_limit = 4
    raw_html_tag: str | None = None
    list_stack: list[tuple[int, int]] = []

    for line in text.splitlines():
        if raw_html_tag is not None:
            if re.search(rf"</\s*{re.escape(raw_html_tag)}\s*>", line, re.I):
                raw_html_tag = None
            continue

        if fence_char is not None:
            closing = re.match(
                rf"^([ \t]*){re.escape(fence_char)}{{{fence_length},}}[ \t]*$",
                line,
            )
            if closing and indent_width(closing.group(1)) <= fence_indent_limit:
                fence_char = None
                fence_length = 0
            continue

        raw_html = re.match(
            r"^ {0,3}<(pre|script|style|textarea)(?:\s|>|$)",
            line,
            re.I,
        )
        if raw_html:
            tag = raw_html.group(1).lower()
            if not re.search(rf"</\s*{re.escape(tag)}\s*>", line, re.I):
                raw_html_tag = tag
            continue

        if not line.strip():
            if not in_indented_code:
                visible.append(line)
            continue

        leading = indent_width(line)
        if in_indented_code:
            if leading >= indented_code_limit:
                continue
            in_indented_code = False

        active_content = max(
            (content for _, content in list_stack if content <= leading),
            default=None,
        )
        opening = re.match(r"^([ \t]*)(`{3,}|~{3,})(.*)$", line)
        if opening:
            marker = opening.group(2)
            base_indent: int | None = None
            if leading <= 3:
                base_indent = 0
            elif active_content is not None and leading - active_content <= 3:
                base_indent = active_content
            if base_indent is not None:
                fence_char = marker[0]
                fence_length = len(marker)
                fence_indent_limit = base_indent + 3
                continue

        list_item = re.match(r"^([ \t]*)([-+*]|\d+[.)])([ \t]+)", line)
        if list_item:
            item_indent = indent_width(list_item.group(1))
            valid_item = item_indent <= 3 or any(
                content <= item_indent for _, content in list_stack
            )
            if valid_item:
                while list_stack and item_indent <= list_stack[-1][0]:
                    list_stack.pop()
                content_indent = (
                    item_indent
                    + len(list_item.group(2))
                    + max(1, indent_width(list_item.group(3)))
                )
                list_stack.append((item_indent, content_indent))
                visible.append(line)
                continue

        active_content = max(
            (content for _, content in list_stack if content <= leading),
            default=None,
        )
        if active_content is not None:
            if leading >= active_content + 4:
                in_indented_code = True
                indented_code_limit = active_content + 4
                continue
            visible.append(line)
            continue

        if leading >= 4:
            in_indented_code = True
            indented_code_limit = 4
            continue

        list_stack.clear()
        visible.append(line)

    return "\n".join(visible)


def section_body(text: str, title: str) -> str | None:
    match = re.search(rf"^##\s+{re.escape(title)}\s*$", text, re.M)
    if not match:
        return None
    tail = text[match.end():]
    next_match = re.search(r"^##\s+", tail, re.M)
    return tail[: next_match.start() if next_match else len(tail)].strip()


def subsection_body(text: str, title: str) -> str | None:
    match = re.search(rf"^###\s+{re.escape(title)}\s*$", text, re.M)
    if not match:
        return None
    tail = text[match.end():]
    next_match = re.search(r"^(?:##|###)\s+", tail, re.M)
    return tail[: next_match.start() if next_match else len(tail)].strip()


def table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def table_separator(line: str) -> bool:
    cells = table_cells(line)
    return bool(cells) and all(
        re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) is not None
        for cell in cells
    )


def table_data_rows(section: str) -> list[list[str]]:
    lines = section.splitlines()
    rows: list[list[str]] = []
    for index, line in enumerate(lines):
        cells = table_cells(line)
        if not cells or table_separator(line) or not any(cells):
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        if next_index < len(lines) and table_separator(lines[next_index]):
            continue
        rows.append(cells)
    return rows


def meaningful(value: str) -> bool:
    text = re.sub(r"<!--.*?-->", "", visible_markdown(value), flags=re.S)
    content: list[str] = []
    data_rows = {tuple(row) for row in table_data_rows(text)}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or re.match(r"^#{1,6}\s+", stripped):
            continue
        cells = table_cells(stripped)
        if cells is not None:
            if tuple(cells) not in data_rows:
                continue
        content.append(stripped)
    return len(" ".join(content)) >= 12


def list_value(metadata: dict, key: str, path: Path) -> list[str]:
    if key not in metadata:
        fail(f"{rel(path)}: missing frontmatter key {key}")
        return []
    value = metadata[key]
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        fail(f"{rel(path)}: frontmatter {key} must be a string list")
        return []
    if len(value) != len(set(value)):
        fail(f"{rel(path)}: frontmatter {key} contains duplicates")
    return value


def exact_ids(text: str, prefix: str) -> set[str]:
    return set(
        re.findall(
            rf"(?<![A-Z0-9-]){re.escape(prefix)}[A-Z0-9-]+(?![A-Z0-9-])",
            text,
        )
    )


def table_ids(section: str, prefix: str) -> set[str]:
    result: set[str] = set()
    for cells in table_data_rows(section):
        candidate = cells[0]
        if re.fullmatch(rf"{re.escape(prefix)}[A-Z0-9-]+", candidate):
            result.add(candidate)
    return result


def spec_ids(change_dir: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted((change_dir / "specs").glob("*.md")):
        if path.name == "README.md":
            continue
        result.update(
            re.findall(
                r"^##\s+(SPEC-[A-Z0-9-]+)(?:\s|$)",
                path.read_text(encoding="utf-8"),
                re.M,
            )
        )
    return result


def change_number(change_id: object) -> int | None:
    if not isinstance(change_id, str):
        return None
    match = re.fullmatch(r"CHG-(\d{4})", change_id)
    return int(match.group(1)) if match else None


def expected_design_status(change_state: str) -> str | None:
    if change_state == "draft":
        return "draft"
    if change_state == "review":
        return "review"
    if change_state in APPROVED_STATES:
        return "approved"
    return None


def spec_gate_approved(change: dict) -> bool:
    gates = change.get("gates")
    if not isinstance(gates, dict):
        return False
    spec_gate = gates.get("spec_review")
    return isinstance(spec_gate, dict) and spec_gate.get("status") == "approved"


def validate_applicability(metadata: dict, path: Path) -> dict:
    applicability = metadata.get("applicability")
    if not isinstance(applicability, dict):
        fail(f"{rel(path)}: applicability must be an object")
        return {}
    missing = set(FACETS) - set(applicability)
    extra = set(applicability) - set(FACETS)
    if missing:
        fail(f"{rel(path)}: missing applicability facets: {', '.join(sorted(missing))}")
    if extra:
        fail(f"{rel(path)}: unknown applicability facets: {', '.join(sorted(extra))}")
    for facet, value in applicability.items():
        if value not in APPLICABILITY_VALUES:
            fail(f"{rel(path)}: applicability {facet} must be required or not-applicable")
    return applicability


def has_id(section: str, prefixes: tuple[str, ...]) -> bool:
    return any(exact_ids(section, prefix) for prefix in prefixes)


def has_na_reason(section: str, facet: str) -> bool:
    for line in section.splitlines():
        match = re.match(
            rf"^\s*N/A:\s*{re.escape(facet)}\s*-\s*(.*)$",
            line,
        )
        if match and len(match.group(1).strip()) >= 5:
            return True
    return False


def validate_linked_rows(
    path: Path,
    section: str,
    existing_specs: set[str],
    declared_tests: set[str],
) -> None:
    for line in section.splitlines():
        cells = table_cells(line)
        sec_references = exact_ids(line, "SEC-")
        test_references = exact_ids(line, "TEST-")
        sec_definition = bool(
            cells and re.fullmatch(r"SEC-[A-Z0-9-]+", cells[0])
        )
        tracked = re.search(
            r"(?<![A-Z0-9-])(?:RULE|INV|CMD|CONSTRAINT)-[A-Z0-9-]+(?![A-Z0-9-])",
            line,
        )
        if not tracked and not sec_definition and not (sec_references and test_references):
            continue
        spec_references = exact_ids(line, "SPEC-")
        unknown_specs = sorted(spec_references - existing_specs)
        unknown_tests = sorted(test_references - declared_tests)
        if unknown_specs:
            fail(f"{rel(path)}: linked row references unknown Spec(s): {', '.join(unknown_specs)}")
        if unknown_tests:
            fail(f"{rel(path)}: linked row references unknown Test(s): {', '.join(unknown_tests)}")
        if re.search(r"(?<![A-Z0-9-])(?:RULE|INV)-[A-Z0-9-]+(?![A-Z0-9-])", line):
            if not spec_references or not test_references:
                fail(f"{rel(path)}: every RULE/INV row must link both SPEC and TEST")
        if re.search(r"(?<![A-Z0-9-])CMD-[A-Z0-9-]+(?![A-Z0-9-])", line):
            if (
                not spec_references
                or not test_references
                or not exact_ids(line, "PERM-")
                or not exact_ids(line, "ERR-")
            ):
                fail(f"{rel(path)}: every CMD row must link SPEC, TEST, PERM and ERR")
        if (
            re.search(r"(?<![A-Z0-9-])CONSTRAINT-[A-Z0-9-]+(?![A-Z0-9-])", line)
            and not test_references
        ):
            fail(f"{rel(path)}: every CONSTRAINT row must link TEST")
        if sec_definition and not test_references:
            fail(f"{rel(path)}: every SEC row must link TEST")


def validate_template() -> None:
    path = ROOT / "changes/_template/design.md"
    if not path.is_file():
        fail("changes/_template/design.md: missing design template")
        return
    metadata, body = read_design(path)
    if metadata is None:
        return
    if not is_version_one(metadata.get("contract_version")):
        fail(f"{rel(path)}: template contract_version must be integer 1")
    if metadata.get("change") != "CHG-0000" or metadata.get("status") != "draft":
        fail(f"{rel(path)}: template must use change CHG-0000 and status draft")
    for key in ("capabilities", "specs", "affected_domains", "decisions"):
        list_value(metadata, key, path)
    validate_applicability(metadata, path)
    open_questions = metadata.get("open_questions")
    if not isinstance(open_questions, int) or isinstance(open_questions, bool) or open_questions < 0:
        fail(f"{rel(path)}: template open_questions must be a non-negative integer")
    visible = visible_markdown(body)
    for title in REQUIRED_SECTIONS:
        if section_body(visible, title) is None:
            fail(f"{rel(path)}: template missing section ## {title}")


def validate_change(change_dir: Path) -> None:
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file():
        return
    change = load_yaml(change_path)
    if change is None:
        return

    number = change_number(change.get("id"))
    contract_version = change.get("design_contract_version")
    if number is not None and number >= REQUIRED_FROM_CHANGE_NUMBER and not is_version_one(contract_version):
        fail(f"{rel(change_path)}: CHG-0006 and later require design_contract_version: integer 1")
        return
    if not is_version_one(contract_version):
        return
    if not design_path.is_file():
        fail(f"{rel(change_dir)}: design contract requires design.md")
        return

    metadata, body = read_design(design_path)
    if metadata is None:
        return
    visible_body = visible_markdown(body)
    if not is_version_one(metadata.get("contract_version")):
        fail(f"{rel(design_path)}: contract_version must be integer 1")

    change_id = change.get("id")
    if metadata.get("change") != change_id:
        fail(f"{rel(design_path)}: frontmatter change must equal {change_id}")

    gate_approved = spec_gate_approved(change)
    design_status = metadata.get("status")
    if design_status not in DESIGN_STATUSES:
        fail(f"{rel(design_path)}: invalid design status")
    expected = "approved" if gate_approved else expected_design_status(str(change.get("status")))
    if expected and design_status != expected:
        fail(
            f"{rel(design_path)}: status must be {expected} when Change is "
            f"{change.get('status')} and Spec Gate approved={gate_approved}"
        )

    references = (
        ("capabilities", "capabilities"),
        ("affected_domains", "affected_domains"),
        ("decisions", "affected_decisions"),
    )
    for design_key, change_key in references:
        actual = list_value(metadata, design_key, design_path)
        expected_values = change.get(change_key, [])
        if not isinstance(expected_values, list) or set(actual) != set(expected_values):
            fail(f"{rel(design_path)}: {design_key} must match change.yaml {change_key}")

    design_specs = list_value(metadata, "specs", design_path)
    existing_specs = spec_ids(change_dir)
    if set(design_specs) != existing_specs:
        fail(f"{rel(design_path)}: specs must exactly match Spec IDs in changes/{change_dir.name}/specs")

    applicability = validate_applicability(metadata, design_path)
    open_questions = metadata.get("open_questions")
    if not isinstance(open_questions, int) or isinstance(open_questions, bool) or open_questions < 0:
        fail(f"{rel(design_path)}: open_questions must be a non-negative integer")
        open_questions = -1

    sections: dict[str, str] = {}
    for title in REQUIRED_SECTIONS:
        value = section_body(visible_body, title)
        if value is None:
            fail(f"{rel(design_path)}: missing section ## {title}")
            value = ""
        sections[title] = value

    review_ready = change.get("status") in ACTIVE_STATES or gate_approved
    if not review_ready:
        return

    forbidden = re.search(
        r"(?<![A-Za-z0-9_])(?:TODO|TBD)(?![A-Za-z0-9_])|待确认|待补充|<!--",
        visible_body,
        re.I,
    )
    if forbidden:
        fail(f"{rel(design_path)}: review-ready design contains placeholder {forbidden.group(0)!r}")
    for title, value in sections.items():
        if not meaningful(value):
            fail(f"{rel(design_path)}: section ## {title} has no meaningful content")

    for facet, (title, prefixes) in FACETS.items():
        value = applicability.get(facet)
        section = sections.get(title, "")
        if value == "required" and not has_id(section, prefixes):
            fail(f"{rel(design_path)}: required facet {facet} needs stable ID {prefixes} in ## {title}")
        if value == "not-applicable" and not has_na_reason(section, facet):
            fail(f"{rel(design_path)}: not-applicable facet {facet} needs a concrete N/A reason in ## {title}")

    test_list = subsection_body(sections["测试 Seam"], "测试清单")
    if test_list is None or not meaningful(test_list):
        fail(f"{rel(design_path)}: missing or empty ### 测试清单")
        test_list = ""
    declared_tests = table_ids(test_list, "TEST-")
    if applicability.get("tests_traceability") == "required" and not declared_tests:
        fail(f"{rel(design_path)}: required tests_traceability needs declared TEST IDs in ### 测试清单")

    for section in sections.values():
        validate_linked_rows(design_path, section, existing_specs, declared_tests)

    trace = subsection_body(sections["测试 Seam"], "Spec 追踪矩阵")
    if trace is None or not meaningful(trace):
        fail(f"{rel(design_path)}: missing or empty ### Spec 追踪矩阵")
        trace = ""

    matrix_specs: set[str] = set()
    for cells in table_data_rows(trace):
        if not cells:
            continue
        spec_id = cells[0]
        if not re.fullmatch(r"SPEC-[A-Z0-9-]+", spec_id):
            continue
        matrix_specs.add(spec_id)
        test_references = exact_ids(" | ".join(cells[1:]), "TEST-")
        if not test_references:
            fail(f"{rel(design_path)}: Spec traceability row {spec_id} must link at least one declared Test")
        unknown_tests = sorted(test_references - declared_tests)
        if unknown_tests:
            fail(f"{rel(design_path)}: Spec traceability row {spec_id} references unknown Test(s): {', '.join(unknown_tests)}")

    unknown_matrix_specs = sorted(matrix_specs - existing_specs)
    if unknown_matrix_specs:
        fail(f"{rel(design_path)}: Spec traceability matrix contains unknown Spec(s): {', '.join(unknown_matrix_specs)}")
    for spec_id in sorted(existing_specs):
        if spec_id not in matrix_specs:
            fail(f"{rel(design_path)}: Spec {spec_id} is missing from the Spec traceability matrix")

    open_ids = exact_ids(visible_body, "OPEN-")
    if open_questions != len(open_ids):
        fail(f"{rel(design_path)}: open_questions={open_questions} but found {len(open_ids)} OPEN IDs")
    if (change.get("status") in APPROVED_STATES or gate_approved) and open_questions != 0:
        fail(f"{rel(design_path)}: approved Change or Spec Gate requires open_questions: 0")


def main() -> int:
    ERRORS.clear()
    validate_template()
    changes_root = ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
                validate_change(path)
    if ERRORS:
        print("Design validation failed:")
        for message in ERRORS:
            print(f"- {message}")
        return 1
    print("Design validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
