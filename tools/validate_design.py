#!/usr/bin/env python3
from __future__ import annotations

import re

import _validate_design_core as core

# CHG-0006 was introduced by diagnostic governance on main before the design
# contract landed. The design contract therefore becomes mandatory at CHG-0007.
core.REQUIRED_FROM_CHANGE_NUMBER = 7

_original_visible_markdown = core.visible_markdown


def visible_markdown(text: str) -> str:
    """Normalize block-quote containers before masking Markdown code blocks."""
    normalized: list[str] = []
    for line in text.splitlines():
        value = line
        while True:
            match = re.match(r"^ {0,3}>[ \t]?", value)
            if not match:
                break
            value = value[match.end():]
        normalized.append(value)
    return _original_visible_markdown("\n".join(normalized))


def validate_linked_rows(
    path,
    section: str,
    existing_specs: set[str],
    declared_tests: set[str],
) -> None:
    """Validate only definition rows whose first table cell is a tracked ID."""
    for line in section.splitlines():
        cells = core.table_cells(line)
        if not cells:
            continue
        definition_id = cells[0]
        match = re.fullmatch(
            r"(RULE|INV|CMD|CONSTRAINT|SEC)-[A-Z0-9-]+",
            definition_id,
        )
        if not match:
            continue

        kind = match.group(1)
        spec_references = core.exact_ids(line, "SPEC-")
        test_references = core.exact_ids(line, "TEST-")
        unknown_specs = sorted(spec_references - existing_specs)
        unknown_tests = sorted(test_references - declared_tests)
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
        if kind in {"RULE", "INV"} and (
            not spec_references or not test_references
        ):
            core.fail(f"{core.rel(path)}: every RULE/INV row must link both SPEC and TEST")
        if kind == "CMD" and (
            not spec_references
            or not test_references
            or not core.exact_ids(line, "PERM-")
            or not core.exact_ids(line, "ERR-")
        ):
            core.fail(f"{core.rel(path)}: every CMD row must link SPEC, TEST, PERM and ERR")
        if kind in {"CONSTRAINT", "SEC"} and not test_references:
            core.fail(f"{core.rel(path)}: every {kind} row must link TEST")


core.visible_markdown = visible_markdown
core.validate_linked_rows = validate_linked_rows


def main() -> int:
    core.ERRORS.clear()
    core.validate_template()
    changes_root = core.ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
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
