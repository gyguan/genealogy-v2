#!/usr/bin/env python3
from __future__ import annotations

import re

import _validate_design_core as core

core.REQUIRED_FROM_CHANGE_NUMBER = 7

_original_visible_markdown = core.visible_markdown
_TRACKED_DEFINITION = re.compile(r"(RULE|INV|CMD|CONSTRAINT|SEC)-[A-Z0-9-]+")
_TRACKED_PREFIXES = ("RULE-", "INV-", "CMD-", "CONSTRAINT-", "SEC-")
_RAW_HTML_BLOCK_TAGS = {
    "address", "article", "aside", "base", "basefont", "blockquote", "body",
    "caption", "center", "col", "colgroup", "dd", "details", "dialog", "dir",
    "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form",
    "frame", "frameset", "h1", "h2", "h3", "h4", "h5", "h6", "head",
    "header", "hr", "html", "iframe", "legend", "li", "link", "main",
    "menu", "menuitem", "nav", "noframes", "ol", "optgroup", "option", "p",
    "param", "search", "section", "summary", "table", "tbody", "td", "tfoot",
    "th", "thead", "title", "tr", "track", "ul",
}
_RAW_HTML_UNTIL_CLOSE = {"pre", "script", "style", "textarea"}
_COMPLETE_HTML_TAG = re.compile(
    r'''^</?[A-Za-z][A-Za-z0-9-]*(?:\s+(?:[^<>"']+|"[^"]*"|'[^']*')*)?\s*/?>\s*$'''
)
_RAW_PLACEHOLDER = re.compile(
    r"(?<![A-Za-z0-9_])(?:TODO|TBD)(?![A-Za-z0-9_])|待确认|待补充",
    re.I,
)


def _update_list_stack(line: str, stack: list[tuple[int, int]]) -> int:
    leading = core.indent_width(line)
    item = re.match(r"^([ \t]*)([-+*]|\d+[.)])([ \t]+)", line)
    if item:
        item_indent = core.indent_width(item.group(1))
        if item_indent <= 3 or any(content <= item_indent for _, content in stack):
            while stack and item_indent <= stack[-1][0]:
                stack.pop()
            content_indent = (
                item_indent
                + len(item.group(2))
                + max(1, core.indent_width(item.group(3)))
            )
            stack.append((item_indent, content_indent))
    return leading


def _relative_base(leading: int, stack: list[tuple[int, int]]) -> int | None:
    if leading <= 3:
        return 0
    active = max((content for _, content in stack if content <= leading), default=None)
    if active is not None and leading - active <= 3:
        return active
    return None


def _fence_open(line: str) -> tuple[str, int] | None:
    match = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", line)
    if not match:
        return None
    marker = match.group(1)
    return marker[0], len(marker)


def _fence_close(line: str, char: str, length: int) -> bool:
    return re.match(
        rf"^[ \t]*{re.escape(char)}{{{length},}}[ \t]*$",
        line,
    ) is not None


def _mask_block_quotes(text: str) -> str:
    output: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    stack: list[tuple[int, int]] = []
    for line in text.splitlines():
        if fence_char is not None:
            output.append(line)
            if _fence_close(line, fence_char, fence_length):
                fence_char = None
                fence_length = 0
            continue
        opening = _fence_open(line)
        if opening:
            fence_char, fence_length = opening
            output.append(line)
            continue
        leading = _update_list_stack(line, stack)
        candidate = line.lstrip(" \t") if _relative_base(leading, stack) is not None else ""
        output.append("" if candidate.startswith(">") else line)
    return "\n".join(output)


def _mask_raw_html_blocks(text: str) -> str:
    output: list[str] = []
    terminator: str | None = None
    until_blank = False
    fence_char: str | None = None
    fence_length = 0
    stack: list[tuple[int, int]] = []

    for line in text.splitlines():
        if fence_char is not None:
            output.append(line)
            if _fence_close(line, fence_char, fence_length):
                fence_char = None
                fence_length = 0
            continue
        opening = _fence_open(line)
        if opening:
            fence_char, fence_length = opening
            output.append(line)
            continue
        if terminator is not None:
            output.append("")
            if terminator.lower() in line.lower():
                terminator = None
            continue
        if until_blank:
            output.append("")
            if not line.strip():
                until_blank = False
            continue

        leading = _update_list_stack(line, stack)
        candidate = line.lstrip(" \t") if _relative_base(leading, stack) is not None else ""
        lowered = candidate.lower()

        if candidate.startswith("<!--"):
            output.append("")
            if "-->" not in candidate[4:]:
                terminator = "-->"
            continue
        if candidate.startswith("<?"):
            output.append("")
            if "?>" not in candidate[2:]:
                terminator = "?>"
            continue
        if candidate.startswith("<![CDATA["):
            output.append("")
            if "]]>" not in candidate[9:]:
                terminator = "]]>"
            continue
        if re.match(r"^<![A-Z]", candidate):
            output.append("")
            if ">" not in candidate[2:]:
                terminator = ">"
            continue

        tag_match = re.match(r"^</?([A-Za-z][A-Za-z0-9-]*)(?:\s|/?>|$)", candidate)
        if tag_match:
            tag = tag_match.group(1).lower()
            if tag in _RAW_HTML_UNTIL_CLOSE:
                output.append("")
                closing = f"</{tag}>"
                if closing not in lowered:
                    terminator = closing
                continue
            if tag in _RAW_HTML_BLOCK_TAGS or _COMPLETE_HTML_TAG.fullmatch(candidate):
                output.append("")
                until_blank = True
                continue
        output.append(line)
    return "\n".join(output)


def visible_markdown(text: str) -> str:
    return _original_visible_markdown(
        _mask_raw_html_blocks(_mask_block_quotes(text))
    )


def table_data_rows(section: str) -> list[list[str]]:
    lines = section.splitlines()
    rows: list[list[str]] = []
    index = 0
    while index + 1 < len(lines):
        header = core.table_cells(lines[index])
        separator = core.table_cells(lines[index + 1])
        if (
            not header
            or not separator
            or not core.table_separator(lines[index + 1])
            or len(header) != len(separator)
        ):
            index += 1
            continue
        row_index = index + 2
        while row_index < len(lines):
            if not lines[row_index].strip():
                break
            cells = core.table_cells(lines[row_index])
            if not cells or core.table_separator(lines[row_index]) or len(cells) != len(header):
                break
            if any(cells):
                rows.append(cells)
            row_index += 1
        index = max(row_index, index + 2)
    return rows


def _tracked_ids(value: str) -> list[str]:
    return sorted(
        {
            identifier
            for prefix in _TRACKED_PREFIXES
            for identifier in core.exact_ids(value, prefix)
        }
    )


def _validate_definition_cells(
    path,
    cells: list[str],
    existing_specs: set[str],
    declared_tests: set[str],
) -> bool:
    definition_id = cells[0]
    tracked = _tracked_ids(definition_id)
    match = re.fullmatch(_TRACKED_DEFINITION, definition_id)
    if tracked and not match:
        core.fail(
            f"{core.rel(path)}: definition ID must be canonical plain text: {tracked[0]}"
        )
        return True
    if not match:
        return False

    row_text = " | ".join(cells)
    kind = match.group(1)
    specs = core.exact_ids(row_text, "SPEC-")
    tests = core.exact_ids(row_text, "TEST-")
    unknown_specs = sorted(specs - existing_specs)
    unknown_tests = sorted(tests - declared_tests)
    if unknown_specs:
        core.fail(
            f"{core.rel(path)}: linked row references unknown Spec(s): {', '.join(unknown_specs)}"
        )
    if unknown_tests:
        core.fail(
            f"{core.rel(path)}: linked row references unknown Test(s): {', '.join(unknown_tests)}"
        )
    if kind in {"RULE", "INV"} and (not specs or not tests):
        core.fail(f"{core.rel(path)}: every RULE/INV row must link both SPEC and TEST")
    if kind == "CMD" and (
        not specs
        or not tests
        or not core.exact_ids(row_text, "PERM-")
        or not core.exact_ids(row_text, "ERR-")
    ):
        core.fail(f"{core.rel(path)}: every CMD row must link SPEC, TEST, PERM and ERR")
    if kind in {"CONSTRAINT", "SEC"} and not tests:
        core.fail(f"{core.rel(path)}: every {kind} row must link TEST")
    return True


def validate_linked_rows(
    path,
    section: str,
    existing_specs: set[str],
    declared_tests: set[str],
) -> None:
    valid_rows = {tuple(cells) for cells in core.table_data_rows(section)}

    for line in section.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("|") and "|" in stripped:
            cells = [cell.strip() for cell in stripped.split("|")]
            if _tracked_ids(cells[0]):
                _validate_definition_cells(path, cells, existing_specs, declared_tests)
                core.fail(
                    f"{core.rel(path)}: definition row must use canonical outer pipes: "
                    f"{_tracked_ids(cells[0])[0]}"
                )
            continue

        cells = core.table_cells(line)
        if cells:
            tracked = _tracked_ids(cells[0])
            if tracked and tuple(cells) not in valid_rows:
                _validate_definition_cells(path, cells, existing_specs, declared_tests)
                core.fail(
                    f"{core.rel(path)}: definition row must belong to a Markdown table: {tracked[0]}"
                )
            continue

        leading = re.match(_TRACKED_DEFINITION, stripped)
        if leading:
            core.fail(
                f"{core.rel(path)}: definition {leading.group(0)} must use a canonical Markdown table row"
            )

    for cells in core.table_data_rows(section):
        _validate_definition_cells(path, cells, existing_specs, declared_tests)


def _review_ready(change: dict) -> bool:
    return change.get("status") in core.ACTIVE_STATES or core.spec_gate_approved(change)


def validate_original_review_markers(change_dir) -> None:
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file() or not design_path.is_file():
        return
    change = core.load_yaml(change_path)
    if change is None or not core.is_version_one(change.get("design_contract_version")):
        return
    metadata, body = core.read_design(design_path)
    if metadata is None or not _review_ready(change):
        return
    if "<!--" in body:
        core.fail(f"{core.rel(design_path)}: review-ready design contains forbidden HTML comment")
    placeholder = _RAW_PLACEHOLDER.search(body)
    if placeholder:
        core.fail(
            f"{core.rel(design_path)}: review-ready design contains placeholder {placeholder.group(0)!r}"
        )


def validate_required_definition_facets(change_dir) -> None:
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file() or not design_path.is_file():
        return
    change = core.load_yaml(change_path)
    if change is None or not core.is_version_one(change.get("design_contract_version")):
        return
    metadata, body = core.read_design(design_path)
    if metadata is None or not _review_ready(change):
        return
    applicability = metadata.get("applicability")
    if not isinstance(applicability, dict):
        return
    visible = core.visible_markdown(body)
    requirements = (
        ("domain_model", "领域与数据影响", r"(?:RULE|INV)-[A-Z0-9-]+", "RULE/INV"),
        ("security_privacy", "安全与隐私", r"SEC-[A-Z0-9-]+", "SEC"),
    )
    for facet, title, pattern, label in requirements:
        if applicability.get(facet) != "required":
            continue
        section = core.section_body(visible, title) or ""
        definitions = {
            cells[0]
            for cells in core.table_data_rows(section)
            if cells and re.fullmatch(pattern, cells[0])
        }
        if not definitions:
            core.fail(
                f"{core.rel(design_path)}: required facet {facet} needs a canonical "
                f"{label} definition row with Spec/Test traceability"
            )


def validate_test_registry(change_dir) -> None:
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file() or not design_path.is_file():
        return
    change = core.load_yaml(change_path)
    if change is None or not core.is_version_one(change.get("design_contract_version")):
        return
    metadata, body = core.read_design(design_path)
    if metadata is None:
        return

    visible = core.visible_markdown(body)
    test_seam = core.section_body(visible, "测试 Seam")
    checklist = core.subsection_body(test_seam or "", "测试清单")
    design_tests = core.table_ids(checklist or "", "TEST-")

    registry_path = change_dir / "tests.yaml"
    if not registry_path.is_file():
        core.fail(f"{core.rel(change_dir)}: design contract requires tests.yaml registry")
        return
    registry = core.load_yaml(registry_path)
    if registry is None:
        return
    entries = registry.get("tests")
    if not isinstance(entries, list):
        core.fail(f"{core.rel(registry_path)}: tests must be a list")
        return

    coverage: dict[str, set[str]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            core.fail(f"{core.rel(registry_path)}: tests[{index}] must declare string id")
            continue
        specs = entry.get("specs")
        if not isinstance(specs, list) or any(not isinstance(spec, str) for spec in specs):
            core.fail(f"{core.rel(registry_path)}: tests[{index}].specs must be a string list")
            continue
        coverage[entry["id"]] = set(specs)

    registry_tests = set(coverage)
    unregistered = sorted(design_tests - registry_tests)
    omitted = sorted(registry_tests - design_tests)
    if unregistered:
        core.fail(
            f"{core.rel(design_path)}: Design test checklist contains unregistered Test(s): "
            f"{', '.join(unregistered)}"
        )
    if omitted:
        core.fail(
            f"{core.rel(design_path)}: tests.yaml Test(s) missing from Design checklist: "
            f"{', '.join(omitted)}"
        )

    trace = core.subsection_body(test_seam or "", "Spec 追踪矩阵")
    for cells in core.table_data_rows(trace or ""):
        if not cells or not re.fullmatch(r"SPEC-[A-Z0-9-]+", cells[0]):
            continue
        spec_id = cells[0]
        if len(cells) != 5:
            core.fail(
                f"{core.rel(design_path)}: Spec traceability row {spec_id} must contain exactly five columns"
            )
            continue
        tests = core.exact_ids(cells[4], "TEST-")
        if not tests:
            core.fail(
                f"{core.rel(design_path)}: Spec traceability row {spec_id} "
                "must link at least one Test in the Test column"
            )
            continue
        unknown = sorted(tests - registry_tests)
        if unknown:
            core.fail(
                f"{core.rel(design_path)}: Spec traceability row {spec_id} "
                f"references unregistered Test(s): {', '.join(unknown)}"
            )
        wrong = sorted(
            test_id
            for test_id in tests
            if test_id in coverage and spec_id not in coverage[test_id]
        )
        if wrong:
            core.fail(
                f"{core.rel(design_path)}: Spec traceability row {spec_id} uses Test(s) "
                f"without registered coverage: {', '.join(wrong)}"
            )


core.visible_markdown = visible_markdown
core.table_data_rows = table_data_rows
core.validate_linked_rows = validate_linked_rows


def main() -> int:
    core.ERRORS.clear()
    core.validate_template()
    changes_root = core.ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
                validate_original_review_markers(path)
                validate_required_definition_facets(path)
                validate_test_registry(path)
                core.validate_change(path)
    if core.ERRORS:
        print("Design validation failed:")
        for message in core.ERRORS:
            print(f"- {message.replace('CHG-0006 and later', 'CHG-0007 and later')}")
        return 1
    print("Design validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
