#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import validate_change_quality as core
from diagnostics import Reporter

SPEC_PATTERN = re.compile(
    r"^#{2,3}[ \t]+(SPEC-[A-Z0-9-]+)(?:[ \t]+[^\r\n]+)?[ \t]*$",
    re.M,
)
SCENARIO_PATTERN = re.compile(
    r"^####[ \t]+Scenario[ \t]+(SCN-[A-Z0-9-]+)(?:[ \t]+[^\r\n]+)?[ \t]*$",
    re.M,
)
TASK_PATTERN = re.compile(
    r"^##[ \t]+(TASK-[A-Z0-9-]+)(?:[ \t]+[^\r\n]+)?[ \t]*$",
    re.M,
)
LEVEL2_PATTERN = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.M)
SPEC_TITLE_PATTERN = re.compile(r"^(SPEC-[A-Z0-9-]+)(?:[ \t]+[^\r\n]+)?$")
FENCE_OPEN_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def strip_fenced_blocks(text: str) -> str:
    """Mask CommonMark fenced blocks while preserving line boundaries."""
    output: list[str] = []
    fence_char: str | None = None
    fence_length = 0
    for line in text.splitlines():
        if fence_char is not None:
            output.append("")
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*",
                line,
            ):
                fence_char = None
                fence_length = 0
            continue
        match = FENCE_OPEN_PATTERN.match(line)
        if match:
            marker = match.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            output.append("")
            continue
        output.append(line)
    return "\n".join(output)


def action_for_spec(text: str, spec_start: int) -> str | None:
    current_action: str | None = None
    for heading in LEVEL2_PATTERN.finditer(text):
        if heading.start() >= spec_start:
            break
        title = heading.group(1).strip()
        if title in core.ACTIONS:
            current_action = title
        elif SPEC_TITLE_PATTERN.fullmatch(title):
            continue
        else:
            current_action = None
    return current_action


def spec_blocks(text: str) -> list[tuple[re.Match[str], str]]:
    specs = list(SPEC_PATTERN.finditer(text))
    level2 = list(LEVEL2_PATTERN.finditer(text))
    result: list[tuple[re.Match[str], str]] = []
    for index, match in enumerate(specs):
        boundaries = [len(text)]
        if index + 1 < len(specs):
            boundaries.append(specs[index + 1].start())
        boundaries.extend(
            heading.start()
            for heading in level2
            if heading.start() > match.start()
        )
        result.append((match, text[match.end():min(boundaries)]))
    return result


def parse_specs(path: Path, reporter: Reporter, strict: bool) -> tuple[set[str], set[str]]:
    if path.name.casefold() == "readme.md":
        return set(), set()
    try:
        text = strip_fenced_blocks(path.read_text(encoding="utf-8"))
    except OSError as exc:
        reporter.error("SPEC-READ-001", f"cannot read Spec: {exc}", core.rel(path))
        return set(), set()

    has_action_heading = any(
        heading.group(1).strip() in core.ACTIONS
        for heading in LEVEL2_PATTERN.finditer(text)
    )
    if strict and not has_action_heading:
        reporter.error(
            "SPEC-FORMAT-001",
            "strict Spec needs at least one ## ADDED/MODIFIED/REMOVED/RENAMED section",
            core.rel(path),
        )

    spec_ids: set[str] = set()
    scenario_ids: set[str] = set()
    for match, block in spec_blocks(text):
        spec_id = match.group(1)
        if strict and action_for_spec(text, match.start()) is None:
            reporter.error(
                "SPEC-FORMAT-003",
                f"{spec_id} must be inside an ADDED/MODIFIED/REMOVED/RENAMED section",
                core.rel(path),
            )
            continue
        if spec_id in spec_ids:
            reporter.error("SPEC-ID-001", f"duplicate Spec id {spec_id}", core.rel(path))
        spec_ids.add(spec_id)

        if strict:
            requirement_match = re.search(
                r"^####[ \t]+Requirement[ \t]*$([\s\S]*?)(?=^####[ \t]+Scenario[ \t]+SCN-|\Z)",
                block,
                re.M,
            )
            if requirement_match is None:
                reporter.error("SPEC-FORMAT-002", f"{spec_id} needs #### Requirement", core.rel(path))
            elif not core.meaningful(requirement_match.group(1)):
                reporter.error(
                    "SPEC-CONTENT-001",
                    f"{spec_id} Requirement has no meaningful content",
                    core.rel(path),
                )

            scenarios = SCENARIO_PATTERN.findall(block)
            if not scenarios:
                reporter.error(
                    "SPEC-SCENARIO-001",
                    f"{spec_id} needs at least one identified #### Scenario SCN-*",
                    core.rel(path),
                )
            for scenario_id in scenarios:
                if scenario_id in scenario_ids:
                    reporter.error(
                        "SPEC-SCENARIO-002",
                        f"duplicate Scenario id {scenario_id}",
                        core.rel(path),
                    )
                scenario_ids.add(scenario_id)
                scenario_match = re.search(
                    rf"^####[ \t]+Scenario[ \t]+{re.escape(scenario_id)}(?:[ \t]+[^\r\n]+)?[ \t]*$([\s\S]*?)(?=^####[ \t]+Scenario[ \t]+SCN-|\Z)",
                    block,
                    re.M,
                )
                scenario_body = scenario_match.group(1) if scenario_match else ""
                for keyword in ("Given", "When", "Then"):
                    if not re.search(rf"^-[ \t]+{keyword}:[ \t]*\S", scenario_body, re.M):
                        reporter.error(
                            "SPEC-SCENARIO-003",
                            f"{scenario_id} needs - {keyword}: with observable content",
                            core.rel(path),
                        )
        elif not core.meaningful(block):
            reporter.error("SPEC-CONTENT-002", f"{spec_id} has no meaningful content", core.rel(path))

    if not spec_ids:
        reporter.error("SPEC-ID-002", "active Change needs at least one Spec requirement", core.rel(path))
    elif not strict:
        if not has_action_heading:
            reporter.warning(
                "SPEC-MIGRATION-001",
                "legacy Spec has no explicit ADDED/MODIFIED/REMOVED/RENAMED section",
                core.rel(path),
            )
        if not SCENARIO_PATTERN.search(text):
            reporter.warning(
                "SPEC-MIGRATION-002",
                "legacy Spec has no machine-traceable Scenario IDs",
                core.rel(path),
            )
    return spec_ids, scenario_ids


def parse_task_fields(path: Path, reporter: Reporter) -> list[dict[str, str]]:
    try:
        text = strip_fenced_blocks(path.read_text(encoding="utf-8"))
    except OSError as exc:
        reporter.error("TASK-READ-001", f"cannot read Tasks: {exc}", core.rel(path))
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
    for match, block in core.split_blocks(TASK_PATTERN, text):
        item = {"id": match.group(1)}
        for field in fields:
            found = re.search(
                rf"^-[ \t]+{re.escape(field)}:[ \t]*(.*?)[ \t]*$",
                block,
                re.M,
            )
            if found:
                item[field] = found.group(1).strip()
        tasks.append(item)
    return tasks


def main() -> int:
    core.SPEC_PATTERN = SPEC_PATTERN
    core.SCENARIO_PATTERN = SCENARIO_PATTERN
    core.TASK_PATTERN = TASK_PATTERN
    core.parse_specs = parse_specs
    core.parse_task_fields = parse_task_fields
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
