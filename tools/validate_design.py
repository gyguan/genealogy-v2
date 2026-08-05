#!/usr/bin/env python3
from __future__ import annotations

import re

import _validate_design_current as current

previous = current.previous
core = current.core


def _html_interrupts_paragraph(value: str) -> bool:
    stripped = value.strip()
    if stripped.startswith(("<!--", "<?", "<![CDATA[")):
        return True
    if re.match(r"^<![A-Z]", stripped):
        return True
    tag_match = re.match(
        r"^</?([A-Za-z][A-Za-z0-9-]*)(?:\s|/?>|$)",
        stripped,
    )
    if not tag_match:
        return False
    tag = tag_match.group(1).lower()
    return tag in previous._RAW_HTML_UNTIL_CLOSE or tag in previous._RAW_HTML_BLOCK_TAGS


def _line_is_block_boundary(line: str) -> bool:
    """Return whether a line can interrupt an already-open paragraph."""
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r"^#{1,6}(?:\s|$)", stripped):
        return True
    if re.fullmatch(r"[=-]+", stripped):
        return True
    if re.fullmatch(r"(?:[-*_][ \t]*){3,}", stripped):
        return True
    # CommonMark permits bullet lists and ordered lists starting at 1 to
    # interrupt paragraphs. Markers such as 2. remain lazy paragraph text.
    if re.match(r"^(?:[-+*]|1[.)])[ \t]+", stripped):
        return True
    if stripped.startswith(">"):
        return True
    if previous._fence_open(stripped):
        return True
    if _html_interrupts_paragraph(stripped):
        return True
    return False


def _paragraph_open_after_line(candidate: str) -> bool:
    """Track rendered paragraph state, including text-bearing list items."""
    stripped = candidate.strip()
    if not stripped:
        return False
    item = re.match(r"^(?:[-+*]|\d+[.)])[ \t]+(.*)$", stripped)
    if item:
        content = item.group(1).strip()
        return bool(content) and not _line_is_block_boundary(content)
    return not _line_is_block_boundary(stripped)


def _mask_block_quotes(text: str) -> str:
    """Mask explicit block quotes and their lazy paragraph continuations."""
    output: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    stack: list[tuple[int, int]] = []
    lazy_quote_paragraph = False

    for line in text.splitlines():
        if fence_char is not None:
            output.append(line)
            if previous._fence_close(line, fence_char, fence_length):
                fence_char = None
                fence_length = 0
            lazy_quote_paragraph = False
            continue

        opening = previous._fence_open(line)
        if opening:
            fence_char, fence_length = opening
            output.append(line)
            lazy_quote_paragraph = False
            continue

        leading = previous._update_list_stack(line, stack)
        candidate = (
            line.lstrip(" \t")
            if previous._relative_base(leading, stack) is not None
            else ""
        )

        if candidate.startswith(">"):
            output.append("")
            quoted = re.sub(r"^(?:>[ \t]?)+", "", candidate)
            lazy_quote_paragraph = bool(quoted.strip()) and not _line_is_block_boundary(
                quoted
            )
            continue

        if lazy_quote_paragraph:
            if not line.strip():
                lazy_quote_paragraph = False
                output.append(line)
                continue
            visible_candidate = candidate or line.lstrip(" \t")
            if _line_is_block_boundary(visible_candidate):
                lazy_quote_paragraph = False
                output.append(line)
                continue
            output.append("")
            continue

        output.append(line)

    return "\n".join(output)


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
            if previous._COMPLETE_HTML_TAG.fullmatch(candidate) and not paragraph_open:
                output.append("")
                until_blank = True
                paragraph_open = False
                continue

        output.append(line)
        paragraph_open = _paragraph_open_after_line(candidate)

    return "\n".join(output)


def table_cells(line: str) -> list[str] | None:
    """Parse an outer-pipe Markdown row while honoring escaped pipes."""
    stripped = line.strip()
    if len(stripped) < 2 or not stripped.startswith("|") or not stripped.endswith("|"):
        return None

    body = stripped[1:-1]
    cells: list[str] = []
    current_cell: list[str] = []

    for char in body:
        if char != "|":
            current_cell.append(char)
            continue

        backslashes = 0
        index = len(current_cell) - 1
        while index >= 0 and current_cell[index] == "\\":
            backslashes += 1
            index -= 1

        if backslashes % 2 == 1:
            current_cell.pop()
            current_cell.append("|")
            continue

        cells.append("".join(current_cell).strip())
        current_cell = []

    cells.append("".join(current_cell).strip())
    return cells


current._line_is_block_boundary = _line_is_block_boundary
current._mask_raw_html_blocks = _mask_raw_html_blocks
previous._mask_block_quotes = _mask_block_quotes
previous._mask_raw_html_blocks = _mask_raw_html_blocks
core.table_cells = table_cells


if __name__ == "__main__":
    raise SystemExit(previous.main())
