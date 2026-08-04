#!/usr/bin/env python3
from __future__ import annotations

import re

import _validate_design_core as core

# CHG-0006 was introduced by diagnostic governance on main before the design
# contract landed. The design contract therefore becomes mandatory at CHG-0007.
core.REQUIRED_FROM_CHANGE_NUMBER = 7

_original_visible_markdown = core.visible_markdown
_TRACKED_DEFINITION = re.compile(
    r"(RULE|INV|CMD|CONSTRAINT|SEC)-[A-Z0-9-]+"
)
_TRACKED_PREFIXES = ("RULE-", "INV-", "CMD-", "CONSTRAINT-", "SEC-")
_RAW_HTML_BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "base",
    "basefont",
    "blockquote",
    "body",
    "caption",
    "center",
    "col",
    "colgroup",
    "dd",
    "details",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "frame",
    "frameset",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "head",
    "header",
    "hr",
    "html",
    "iframe",
    "legend",
    "li",
    "link",
    "main",
    "menu",
    "menuitem",
    "nav",
    "noframes",
    "ol",
    "optgroup",
    "option",
    "p",
    "param",
    "search",
    "section",
    "summary",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "title",
    "tr",
    "track",
    "ul",
}
_RAW_HTML_UNTIL_CLOSE = {"pre", "script", "style", "textarea"}
_COMPLETE_HTML_TAG = re.compile(
    r"^</?[A-Za-z][A-Za-z0-9-]*(?:\s+[^<>]*?)?\s*/?>\s*$"
)


def _mask_raw_html_blocks(text: str) -> str:
    """Mask CommonMark raw HTML blocks without inspecting fenced examples."""
    masked: list[str] = []
    terminator: str | None = None
    until_blank = False
    fence_char: str | None = None
    fence_length = 0

    for line in text.splitlines():
        if fence_char is not None:
            masked.append(line)
            closing = re.match(
                rf"^[ \t]*{re.escape(fence_char)}{{{fence_length},}}[ \t]*$",
                line,
            )
            if closing:
                fence_char = None
                fence_length = 0
            continue

        opening = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", line)
        if opening:
            marker = opening.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            masked.append(line)
            continue

        if terminator is not None:
            masked.append("")
            if terminator.lower() in line.lower():
                terminator = None
            continue

        if until_blank:
            if not line.strip():
                until_blank = False
            masked.append("")
            continue

        match = re.match(r"^ {0,3}(.*)$", line)
        candidate = match.group(1) if match else ""
        lowered = candidate.lower()

        if candidate.startswith("<!--"):
            masked.append("")
            if "-->" not in candidate[4:]:
                terminator = "-->"
            continue
        if candidate.startswith("<?"):
            masked.append("")
            if "?>" not in candidate[2:]:
                terminator = "?>"
            continue
        if candidate.startswith("<![CDATA["):
            masked.append("")
            if "]]>" not in candidate[9:]:
                terminator = "]]>"
            continue
        if re.match(r"^<![A-Z]", candidate):
            masked.append("")
            if ">" not in candidate[2:]:
                terminator = ">"
            continue

        tag_match = re.match(r"^</?([A-Za-z][A-Za-z0-9-]*)(?:\s|/?>|$)", candidate)
        if tag_match:
            tag = tag_match.group(1).lower()
            if tag in _RAW_HTML_UNTIL_CLOSE:
                masked.append("")
                closing = f"</{tag}>"
                if closing not in lowered:
                    terminator = closing
                continue
            if tag in _RAW_HTML_BLOCK_TAGS:
                masked.append("")
                until_blank = True
                continue
            if _COMPLETE_HTML_TAG.fullmatch(candidate):
                masked.append("")
                until_blank = True
                continue

        masked.append(line)

    return "\n".join(masked)


def visible_markdown(text: str) -> str:
    """Exclude block quotes and all raw HTML blocks before Markdown parsing."""
    normalized: list[str] = []
    for line in text.splitlines():
        if re.match(r"^ {0,3}>", line):
            normalized.append("")
        else:
            normalized.append(line)
    return _original_visible_markdown(_mask_raw_html_blocks("\n".join(normalized)))


def validate_original_review_markers(change_dir) -> None:
    """Reject template comments before structural masking hides them."""
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file() or not design_path.is_file():
        return
    change = core.load_yaml(change_path)
    if change is None or not core.is_version_one(
        change.get("design_contract_version")
    ):
        return
    metadata, body = core.read_design(design_path)
    if metadata is None:
        return
    review_ready = (
        change.get("status") in core.ACTIVE_STATES
        or core.spec_gate_approved(change)
    )
    if review_ready and "<!--" in body:
        core.fail(
            f"{core.rel(design_path)}: review-ready design contains "
            "forbidden HTML comment"
        )


def validate_required_domain_definitions(change_dir) -> None:
    """Require a required domain facet to use traceable RULE/INV rows."""
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file() or not design_path.is_file():
        return
    change = core.load_yaml(change_path)
    if change is None or not core.is_version_one(
        change.get("design_contract_version")
    ):
        return
    metadata, body = core.read_design(design_path)
    if metadata is None:
        return
    review_ready = (
        change.get("status") in core.ACTIVE_STATES
        or core.spec_gate_approved(change)
    )
    applicability = metadata.get("applicability")
    if (
        not review_ready
        or not isinstance(applicability, dict)
        or applicability.get("domain_model") != "required"
    ):
        return

    visible = core.visible_markdown(body)
    domain_section = core.section_body(visible, "领域与数据影响") or ""
    definitions: set[str] = set()
    for line in domain_section.splitlines():
        cells = core.table_cells(line)
        if cells and re.fullmatch(r"(?:RULE|INV)-[A-Z0-9-]+", cells[0]):
            definitions.add(cells[0])
    if not definitions:
        core.fail(
            f"{core.rel(design_path)}: required facet domain_model needs a "
            "canonical RULE/INV definition row with Spec and Test links"
        )


def validate_linked_rows(
    path,
    section: str,
    existing_specs: set[str],
    declared_tests: set[str],
) -> None:
    """Validate canonical definition rows whose first table cell is a tracked ID."""
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") and "|" in stripped:
            first_cell = stripped.split("|", 1)[0].strip()
            tracked_ids = sorted(
                {
                    tracked_id
                    for prefix in _TRACKED_PREFIXES
                    for tracked_id in core.exact_ids(first_cell, prefix)
                }
            )
            if tracked_ids:
                core.fail(
                    f"{core.rel(path)}: definition row must use canonical "
                    f"outer pipes: {tracked_ids[0]}"
                )
                continue

        cells = core.table_cells(line)
        if not cells:
            continue
        definition_id = cells[0]
        tracked_ids = sorted(
            {
                tracked_id
                for prefix in _TRACKED_PREFIXES
                for tracked_id in core.exact_ids(definition_id, prefix)
            }
        )
        match = re.fullmatch(_TRACKED_DEFINITION, definition_id)
        if tracked_ids and not match:
            core.fail(
                f"{core.rel(path)}: definition ID must be canonical plain text: "
                f"{tracked_ids[0]}"
            )
            continue
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


def validate_test_registry(change_dir) -> None:
    """Require Design tests and Spec coverage to match the formal registry."""
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.md"
    if not change_path.is_file() or not design_path.is_file():
        return

    change = core.load_yaml(change_path)
    if change is None or not core.is_version_one(
        change.get("design_contract_version")
    ):
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
        core.fail(
            f"{core.rel(change_dir)}: design contract requires tests.yaml registry"
        )
        return
    registry = core.load_yaml(registry_path)
    if registry is None:
        return
    entries = registry.get("tests")
    if not isinstance(entries, list):
        core.fail(f"{core.rel(registry_path)}: tests must be a list")
        return

    registry_coverage: dict[str, set[str]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            core.fail(
                f"{core.rel(registry_path)}: tests[{index}] must declare string id"
            )
            continue
        specs = entry.get("specs")
        if not isinstance(specs, list) or any(
            not isinstance(spec_id, str) for spec_id in specs
        ):
            core.fail(
                f"{core.rel(registry_path)}: tests[{index}].specs must be a string list"
            )
            continue
        registry_coverage[entry["id"]] = set(specs)

    registry_tests = set(registry_coverage)
    unregistered = sorted(design_tests - registry_tests)
    omitted = sorted(registry_tests - design_tests)
    if unregistered:
        core.fail(
            f"{core.rel(design_path)}: Design test checklist contains "
            f"unregistered Test(s): {', '.join(unregistered)}"
        )
    if omitted:
        core.fail(
            f"{core.rel(design_path)}: tests.yaml Test(s) missing from "
            f"Design checklist: {', '.join(omitted)}"
        )

    trace = core.subsection_body(test_seam or "", "Spec 追踪矩阵")
    for cells in core.table_data_rows(trace or ""):
        if not cells or not re.fullmatch(r"SPEC-[A-Z0-9-]+", cells[0]):
            continue
        spec_id = cells[0]
        test_references = core.exact_ids(" | ".join(cells[1:]), "TEST-")
        wrong_coverage = sorted(
            test_id
            for test_id in test_references
            if test_id in registry_coverage
            and spec_id not in registry_coverage[test_id]
        )
        if wrong_coverage:
            core.fail(
                f"{core.rel(design_path)}: Spec traceability row {spec_id} "
                f"uses Test(s) without registered coverage: "
                f"{', '.join(wrong_coverage)}"
            )


core.visible_markdown = visible_markdown
core.validate_linked_rows = validate_linked_rows


def main() -> int:
    core.ERRORS.clear()
    core.validate_template()
    changes_root = core.ROOT / "changes"
    if changes_root.exists():
        for path in sorted(changes_root.iterdir()):
            if path.is_dir() and path.name != "_template":
                validate_original_review_markers(path)
                validate_required_domain_definitions(path)
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
