#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

import validate_design_machine_core as core

PLACEHOLDER_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:TODO|TBD|FIXME)(?![A-Za-z0-9_])"
    r"|待确认|待补充|待完善|待明确|尚未确定|暂未确定"
)
STABLE_ID_PATTERN = re.compile(
    r"(?<![A-Z0-9-])(?:SPEC|SCN|TASK|TEST|FACT|ASM|OPEN|FLOW|UC|MODEL|RULE|INV|STATE|CMD|DATA|CONSTRAINT|API|UI|EVENT|MIG|NFR|SEC|MODULE|FAIL|TRACE)-[A-Z0-9-]+(?![A-Z0-9-])"
)
FORBIDDEN_ID_TOKENS = {
    "REPLACE-ME",
    "EXAMPLE",
    "SAMPLE",
    "TEMPLATE",
    "PLACEHOLDER",
    "XXXX",
}


def walk_strings(value: Any, location: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{location}[{index}]")
    elif isinstance(value, str):
        yield location, value


def placeholder_identifier(value: str) -> bool:
    normalized = value.upper()
    return any(token in normalized for token in FORBIDDEN_ID_TOKENS) or bool(
        re.search(r"(?:^|-)0000(?:-|$)", normalized)
    )


def validate_review_ready_placeholders(change_dir: Path) -> None:
    change_path = change_dir / "change.yaml"
    design_path = change_dir / "design.yaml"
    if not change_path.is_file() or not design_path.is_file():
        return
    try:
        change = yaml.safe_load(change_path.read_text(encoding="utf-8"))
        design = yaml.safe_load(design_path.read_text(encoding="utf-8"))
    except Exception:
        return  # Structural validation reports malformed YAML.
    if not isinstance(change, dict) or not isinstance(design, dict):
        return
    if not core.is_version_one(change.get("design_machine_contract_version")):
        return
    review_ready = change.get("status") in core.ACTIVE_STATES or core.spec_gate_approved(change)
    if not review_ready:
        return
    for location, text in walk_strings(design):
        if PLACEHOLDER_PATTERN.search(text):
            core.fail(
                f"{core.rel(design_path)}: {location} contains unresolved placeholder: {text!r}"
            )
        for identifier in STABLE_ID_PATTERN.findall(text):
            if placeholder_identifier(identifier):
                core.fail(
                    f"{core.rel(design_path)}: {location} contains template identifier {identifier}"
                )


def main() -> int:
    core.ERRORS.clear()
    core.validate_template()
    for change_dir in sorted((core.ROOT / "changes").glob("CHG-*")):
        if change_dir.is_dir():
            core.validate_change(change_dir)
            validate_review_ready_placeholders(change_dir)
    if core.ERRORS:
        print("Machine design validation failed:")
        for error in core.ERRORS:
            print(f"- {error}")
        return 1
    print("Machine design validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
