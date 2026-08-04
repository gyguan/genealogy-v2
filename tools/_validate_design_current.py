#!/usr/bin/env python3
from __future__ import annotations

import re

import _validate_design_previous as previous

core = previous.core


def _line_is_block_boundary(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r"^#{1,6}(?:\s|$)", stripped):
        return True
    if re.fullmatch(r"(?:[-*_][ \t]*){3,}", stripped):
        return True
    return False


def _mask_raw_html_blocks(text: str) -> str:
    """Mask raw HTML while respecting fenced code, lists and open paragraphs."""
    output: list[str] = []
    terminator: str | None = None
    until_blank = False
    fence_char: str | None = None
    fence_length = 0
    stack: list[tuple[int, int]] = []
    paragraph_open = False

    for line in text.splitlines():
        if fence_char is not None:
            output.append(line)
            if previous._fence_close(line, fence_char, fence_length):
                fence_char = None
                fence_length = 0
            paragraph_open = False
            continue

        opening = previous._fence_open(line)
        if opening:
            fence_char, fence_length = opening
            output.append(line)
            paragraph_open = False
            continue

        if terminator is not None:
            output.append("")
            if terminator.lower() in line.lower():
                terminator = None
            paragraph_open = False
            continue

        if until_blank:
            output.append("")
            if not line.strip():
                until_blank = False
            paragraph_open = False
            continue

        leading = previous._update_list_stack(line, stack)
        candidate = (
            line.lstrip(" \t")
            if previous._relative_base(leading, stack) is not None
            else ""
        )
        lowered = candidate.lower()

        if candidate.startswith("<!--"):
            output.append("")
            if "-->" not in candidate[4:]:
                terminator = "-->"
            paragraph_open = False
            continue
        if candidate.startswith("<?"):
            output.append("")
            if "?>" not in candidate[2:]:
                terminator = "?>"
            paragraph_open = False
            continue
        if candidate.startswith("<![CDATA["):
            output.append("")
            if "]]>" not in candidate[9:]:
                terminator = "]]>"
            paragraph_open = False
            continue
        if re.match(r"^<![A-Z]", candidate):
            output.append("")
            if ">" not in candidate[2:]:
                terminator = ">"
            paragraph_open = False
            continue

        tag_match = re.match(
            r"^</?([A-Za-z][A-Za-z0-9-]*)(?:\s|/?>|$)",
            candidate,
        )
        if tag_match:
            tag = tag_match.group(1).lower()
            if tag in previous._RAW_HTML_UNTIL_CLOSE:
                output.append("")
                closing = f"</{tag}>"
                if closing not in lowered:
                    terminator = closing
                paragraph_open = False
                continue
            if tag in previous._RAW_HTML_BLOCK_TAGS:
                output.append("")
                until_blank = True
                paragraph_open = False
                continue
            if (
                previous._COMPLETE_HTML_TAG.fullmatch(candidate)
                and not paragraph_open
            ):
                output.append("")
                until_blank = True
                paragraph_open = False
                continue

        output.append(line)
        paragraph_open = not _line_is_block_boundary(line)

    return "\n".join(output)


def table_records(section: str) -> list[tuple[list[str], list[str]]]:
    """Return headers and rows from actual Markdown tables."""
    lines = section.splitlines()
    records: list[tuple[list[str], list[str]]] = []
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
            if (
                not cells
                or core.table_separator(lines[row_index])
                or len(cells) != len(header)
            ):
                break
            if any(cells):
                records.append((header, cells))
            row_index += 1
        index = max(row_index, index + 2)
    return records


def table_data_rows(section: str) -> list[list[str]]:
    return [cells for _, cells in table_records(section)]


def _normalized_header(value: str) -> str:
    return re.sub(r"[\s/_-]+", "", value).lower()


def _column_text(
    header: list[str],
    cells: list[str],
    *tokens: str,
) -> str:
    normalized_tokens = tuple(_normalized_header(token) for token in tokens)
    for index, label in enumerate(header):
        normalized = _normalized_header(label)
        if any(token in normalized for token in normalized_tokens):
            return cells[index] if index < len(cells) else ""
    return ""


def _validate_definition_cells(
    path,
    cells: list[str],
    existing_specs: set[str],
    declared_tests: set[str],
    header: list[str] | None = None,
) -> bool:
    definition_id = cells[0]
    tracked = previous._tracked_ids(definition_id)
    match = re.fullmatch(previous._TRACKED_DEFINITION, definition_id)
    if tracked and not match:
        core.fail(
            f"{core.rel(path)}: definition ID must be canonical plain text: "
            f"{tracked[0]}"
        )
        return True
    if not match:
        return False

    kind = match.group(1)
    if header is None:
        spec_text = test_text = permission_text = error_text = " | ".join(cells)
    else:
        spec_text = _column_text(header, cells, "Spec")
        test_text = _column_text(header, cells, "Test", "测试")
        permission_text = _column_text(header, cells, "PERM", "权限")
        error_text = _column_text(header, cells, "ERR", "失败码", "错误码", "错误")

    specs = core.exact_ids(spec_text, "SPEC-")
    tests = core.exact_ids(test_text, "TEST-")
    permissions = core.exact_ids(permission_text, "PERM-")
    errors = core.exact_ids(error_text, "ERR-")

    unknown_specs = sorted(specs - existing_specs)
    unknown_tests = sorted(tests - declared_tests)
    if unknown_specs:
        core.fail(
            f"{core.rel(path)}: linked row references unknown Spec(s): "
            f"{', '.join(unknown_specs)}"
        )
    if unknown_tests:
        core.fail(
            f"{core.rel(path)}: linked row references unknown Test(s): "
            f"{', '.join(unknown_tests)}"
        )
    if kind in {"RULE", "INV"} and (not specs or not tests):
        core.fail(
            f"{core.rel(path)}: every RULE/INV row must link both SPEC and TEST"
        )
    if kind == "CMD" and (
        not specs or not tests or not permissions or not errors
    ):
        core.fail(
            f"{core.rel(path)}: every CMD row must link SPEC, TEST, PERM and ERR"
        )
    if kind in {"CONSTRAINT", "SEC"} and not tests:
        core.fail(f"{core.rel(path)}: every {kind} row must link TEST")
    return True


def validate_linked_rows(
    path,
    section: str,
    existing_specs: set[str],
    declared_tests: set[str],
) -> None:
    records = table_records(section)
    headers_by_row = {tuple(cells): header for header, cells in records}

    for line in section.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("|") and "|" in stripped:
            cells = [cell.strip() for cell in stripped.split("|")]
            tracked = previous._tracked_ids(cells[0])
            if tracked:
                _validate_definition_cells(
                    path,
                    cells,
                    existing_specs,
                    declared_tests,
                )
                core.fail(
                    f"{core.rel(path)}: definition row must use canonical "
                    f"outer pipes: {tracked[0]}"
                )
            continue

        cells = core.table_cells(line)
        if cells:
            tracked = previous._tracked_ids(cells[0])
            if tracked and tuple(cells) not in headers_by_row:
                _validate_definition_cells(
                    path,
                    cells,
                    existing_specs,
                    declared_tests,
                )
                core.fail(
                    f"{core.rel(path)}: definition row must belong to a "
                    f"Markdown table: {tracked[0]}"
                )
            continue

        leading = re.match(previous._TRACKED_DEFINITION, stripped)
        if leading:
            core.fail(
                f"{core.rel(path)}: definition {leading.group(0)} must use a "
                "canonical Markdown table row"
            )

    for header, cells in records:
        _validate_definition_cells(
            path,
            cells,
            existing_specs,
            declared_tests,
            header,
        )


previous._mask_raw_html_blocks = _mask_raw_html_blocks
previous.table_records = table_records
previous.table_data_rows = table_data_rows
previous._validate_definition_cells = _validate_definition_cells
previous.validate_linked_rows = validate_linked_rows
core.table_data_rows = table_data_rows
core.validate_linked_rows = validate_linked_rows


if __name__ == "__main__":
    raise SystemExit(previous.main())
