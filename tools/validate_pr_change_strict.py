#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

import yaml

import validate_pr_change as core
from diagnostics import Reporter

FRONTMATTER_PATTERN = re.compile(
    r"\A---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|\Z)"
)
DECISION_TYPE_TO_CHANGE = {
    "product": "product",
    "domain": "domain",
    "engineering": "engineering",
    "governance": "governance",
    "security": "security",
}


def decision_change_types(root: Path, path: str, reporter: Reporter) -> set[str]:
    file_path = root / path
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        reporter.error(
            "PR-DECISION-001",
            f"cannot read Decision metadata: {exc}",
            path,
        )
        return set()
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        reporter.error("PR-DECISION-002", "Decision needs YAML frontmatter with type", path)
        return set()
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        reporter.error("PR-DECISION-003", f"invalid Decision frontmatter: {exc}", path)
        return set()
    decision_type = metadata.get("type") if isinstance(metadata, dict) else None
    required = DECISION_TYPE_TO_CHANGE.get(decision_type)
    if required is None:
        reporter.error(
            "PR-DECISION-004",
            f"unsupported Decision type {decision_type!r}",
            path,
        )
        return set()
    return {required}


def required_change_types(root: Path, path: str, reporter: Reporter) -> set[str]:
    if path.startswith("product/"):
        return {"product"}
    if path.startswith("domains/"):
        return {"domain"}
    if path.startswith("decisions/"):
        return decision_change_types(root, path, reporter)
    if path == "SECURITY.md":
        return {"security"}
    if (
        path.startswith("tools/")
        or path.startswith(".github/")
        or path.startswith("skills/")
        or path.startswith("changes/_template/")
        or path in {"AGENTS.md", "README.md", "changes/README.md"}
    ):
        return {"governance", "engineering"}
    return {"engineering", "domain", "security"}


def validate_declared_scope(
    root: Path,
    body: str,
    changed_files: list[str],
    reporter: Reporter,
) -> dict[str, dict]:
    change_ids = core.extract_change_ids(body)
    if not change_ids:
        reporter.error(
            "PR-BODY-001",
            "PR body must declare at least one Change using '- Change ID：CHG-xxxx'",
        )
        return {}

    metadata = {
        change_id: core.load_change_metadata(root, change_id, reporter)
        for change_id in sorted(change_ids)
    }
    declared_types = {
        value.get("change_type")
        for value in metadata.values()
        if isinstance(value.get("change_type"), str)
    }

    for path in changed_files:
        path_change_id = core.change_id_from_path(path)
        if path_change_id is not None:
            if path_change_id not in change_ids:
                reporter.error(
                    "PR-SCOPE-001",
                    f"changed Change asset {path} is not declared in the PR body",
                    path,
                )
            continue
        required = required_change_types(root, path, reporter)
        if not required:
            continue
        if not (declared_types & required):
            reporter.error(
                "PR-SCOPE-002",
                f"file requires one of Change types {sorted(required)}, declared types are {sorted(declared_types)}",
                path,
            )

    for change_id, value in metadata.items():
        state = value.get("status")
        if state not in {"implementing", "completed"}:
            reporter.warning(
                "PR-STATE-001",
                f"{change_id} is {state}; reviewer must confirm the PR is appropriate for the current phase",
            )
        if value.get("quality_policy") != "strict":
            reporter.warning(
                "PR-MIGRATION-001",
                f"{change_id} does not opt into quality_policy: strict",
            )

    reporter.review(
        "REVIEW-PR-001",
        "Reviewer must decide whether the declared Change scope is semantically sufficient; path classification only proves minimum traceability.",
    )
    return metadata


def main() -> int:
    core.validate_declared_scope = validate_declared_scope
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
