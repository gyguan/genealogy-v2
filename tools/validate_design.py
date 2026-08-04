#!/usr/bin/env python3
from __future__ import annotations

import re

import _validate_design_current as current

previous = current.previous


def _line_is_block_boundary(line: str) -> bool:
    """Return whether a line closes or interrupts an ordinary paragraph."""
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r"^#{1,6}(?:\s|$)", stripped):
        return True
    if re.fullmatch(r"[=-]+", stripped):
        return True
    if re.fullmatch(r"(?:[-*_][ \t]*){3,}", stripped):
        return True
    if re.match(r"^(?:[-+*]|\d+[.)])\s+", stripped):
        return True
    if stripped.startswith(">"):
        return True
    if previous._fence_open(stripped):
        return True
    if re.match(r"^</?[A-Za-z]", stripped):
        return True
    return False


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


current._line_is_block_boundary = _line_is_block_boundary
previous._mask_block_quotes = _mask_block_quotes


if __name__ == "__main__":
    raise SystemExit(previous.main())
