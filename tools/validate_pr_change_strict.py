#!/usr/bin/env python3
from __future__ import annotations

import base64
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

import validate_pr_change as core
from diagnostics import Reporter

FRONTMATTER_PATTERN = re.compile(
    r"\A---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|\Z)"
)
FORMAL_DECISION_PATTERN = re.compile(r"^decisions/(DEC-\d{4})-[^/]+\.md$")
FORMAL_DOMAIN_PATTERN = re.compile(r"^domains/([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
CAPABILITY_FILE_PATTERN = re.compile(r"^product/capabilities/[^/]+\.yaml$")
DECISION_TYPE_TO_CHANGES = {
    "product": {"product"},
    "domain": {"domain"},
    "architecture": {"engineering"},
    "compliance": {"governance", "security"},
}


def parse_decision_change_types(text: str, path: str, reporter: Reporter) -> set[str]:
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
    required = DECISION_TYPE_TO_CHANGES.get(decision_type)
    if required is None:
        reporter.error(
            "PR-DECISION-004",
            f"unsupported Decision type {decision_type!r}; expected one of {sorted(DECISION_TYPE_TO_CHANGES)}",
            path,
        )
        return set()
    return set(required)


def decode_contents_payload(payload: Any) -> str:
    if not isinstance(payload, dict):
        raise TypeError("GitHub contents response must be an object")
    content = payload.get("content")
    encoding = payload.get("encoding")
    if not isinstance(content, str) or encoding != "base64":
        raise TypeError("GitHub contents response must contain base64 content")
    return base64.b64decode(content).decode("utf-8")


def changed_file_entries(files: list[dict] | list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for item in core.normalize_changed_files(files):
        filename = item["filename"]
        status = item.get("status") or "modified"
        current = dict(item)
        current["path"] = filename
        current["source"] = "base" if status == "removed" else "head"
        entries.append(current)
        if status == "renamed":
            previous = item.get("previous_filename")
            if isinstance(previous, str):
                old = dict(item)
                old["path"] = previous
                old["source"] = "base"
                entries.append(old)
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        key = (entry["path"], entry["source"])
        if key not in seen:
            seen.add(key)
            result.append(entry)
    return result


def read_repository_text(
    root: Path,
    path: str,
    source: str,
    reporter: Reporter,
    *,
    repo: str | None,
    token: str | None,
    base_sha: str | None,
    embedded: str | None = None,
    diagnostic: str = "PR-ASSET-READ-001",
) -> str | None:
    if source == "head":
        try:
            return (root / path).read_text(encoding="utf-8")
        except OSError as exc:
            reporter.error(diagnostic, f"cannot read current asset: {exc}", path)
            return None
    if isinstance(embedded, str):
        return embedded
    if not all((repo, token, base_sha)):
        reporter.error(
            diagnostic,
            "cannot read historical asset without repository, token and base SHA",
            path,
        )
        return None
    try:
        payload = core.api(
            f"https://api.github.com/repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(base_sha, safe='')}",
            token,
        )
        return decode_contents_payload(payload)
    except Exception as exc:  # normalized into a deterministic diagnostic
        reporter.error(diagnostic, f"cannot read historical asset: {exc}", path)
        return None


def read_decision_text(
    root: Path,
    entry: dict[str, Any],
    reporter: Reporter,
    *,
    repo: str | None,
    token: str | None,
    base_sha: str | None,
) -> str | None:
    return read_repository_text(
        root,
        entry["path"],
        entry.get("source") or "head",
        reporter,
        repo=repo,
        token=token,
        base_sha=base_sha,
        embedded=entry.get("base_content"),
        diagnostic="PR-DECISION-001",
    )


def decision_change_types(
    root: Path,
    entry: dict[str, Any],
    reporter: Reporter,
    *,
    repo: str | None = None,
    token: str | None = None,
    base_sha: str | None = None,
) -> set[str]:
    text = read_decision_text(
        root,
        entry,
        reporter,
        repo=repo,
        token=token,
        base_sha=base_sha,
    )
    return parse_decision_change_types(text, entry["path"], reporter) if text is not None else set()


def required_change_types(
    root: Path,
    path: str,
    reporter: Reporter,
    *,
    entry: dict[str, Any] | None = None,
    repo: str | None = None,
    token: str | None = None,
    base_sha: str | None = None,
) -> set[str]:
    if path.startswith("product/"):
        return {"product"}
    if path.startswith("domains/"):
        return {"domain"}
    if FORMAL_DECISION_PATTERN.fullmatch(path):
        return decision_change_types(
            root,
            entry or {"path": path, "source": "head"},
            reporter,
            repo=repo,
            token=token,
            base_sha=base_sha,
        )
    if path.startswith("decisions/"):
        return {"governance"}
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


def declared_values(metadata: dict[str, dict], field: str) -> set[str]:
    result: set[str] = set()
    for value in metadata.values():
        items = value.get(field)
        if isinstance(items, list):
            result.update(item for item in items if isinstance(item, str))
    return result


def capability_records(text: str, path: str, reporter: Reporter) -> dict[str, Any]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        reporter.error("PR-CAPABILITY-READ-001", f"invalid capability YAML: {exc}", path)
        return {}
    group = data.get("group") if isinstance(data, dict) else None
    items = group.get("capabilities") if isinstance(group, dict) else None
    if not isinstance(items, list):
        reporter.error("PR-CAPABILITY-READ-002", "capability file needs group.capabilities list", path)
        return {}
    result: dict[str, Any] = {}
    for item in items:
        capability_id = item.get("id") if isinstance(item, dict) else None
        if isinstance(capability_id, str):
            result[capability_id] = item
    return result


def changed_capability_ids(
    root: Path,
    item: dict[str, Any],
    reporter: Reporter,
    *,
    repo: str | None,
    token: str | None,
    base_sha: str | None,
) -> set[str]:
    status = item.get("status") or "modified"
    head_path = item.get("filename")
    base_path = item.get("previous_filename") if status == "renamed" else head_path
    head: dict[str, Any] = {}
    base: dict[str, Any] = {}

    if status != "removed" and isinstance(head_path, str) and CAPABILITY_FILE_PATTERN.fullmatch(head_path):
        text = read_repository_text(
            root,
            head_path,
            "head",
            reporter,
            repo=repo,
            token=token,
            base_sha=base_sha,
            diagnostic="PR-CAPABILITY-READ-001",
        )
        if text is not None:
            head = capability_records(text, head_path, reporter)

    if status != "added" and isinstance(base_path, str) and CAPABILITY_FILE_PATTERN.fullmatch(base_path):
        text = read_repository_text(
            root,
            base_path,
            "base",
            reporter,
            repo=repo,
            token=token,
            base_sha=base_sha,
            embedded=item.get("base_content"),
            diagnostic="PR-CAPABILITY-READ-001",
        )
        if text is not None:
            base = capability_records(text, base_path, reporter)

    return {
        capability_id
        for capability_id in set(head) | set(base)
        if head.get(capability_id) != base.get(capability_id)
    }


def validate_exact_asset_scope(
    root: Path,
    files: list[dict] | list[str],
    metadata: dict[str, dict],
    reporter: Reporter,
    *,
    repo: str | None,
    token: str | None,
    base_sha: str | None,
) -> None:
    domains = declared_values(metadata, "affected_domains")
    decisions = declared_values(metadata, "affected_decisions")
    capabilities = declared_values(metadata, "capabilities")

    seen_paths: set[str] = set()
    for entry in changed_file_entries(files):
        path = entry["path"]
        if path in seen_paths:
            continue
        seen_paths.add(path)
        domain_match = FORMAL_DOMAIN_PATTERN.fullmatch(path)
        if domain_match and domain_match.group(1) not in domains:
            reporter.error(
                "PR-DOMAIN-SCOPE-001",
                f"changed Domain {domain_match.group(1)} is not declared in affected_domains",
                path,
            )
        decision_match = FORMAL_DECISION_PATTERN.fullmatch(path)
        if decision_match and decision_match.group(1) not in decisions:
            reporter.error(
                "PR-DECISION-SCOPE-001",
                f"changed Decision {decision_match.group(1)} is not declared in affected_decisions",
                path,
            )

    for item in core.normalize_changed_files(files):
        paths = [item.get("filename"), item.get("previous_filename")]
        if not any(isinstance(path, str) and CAPABILITY_FILE_PATTERN.fullmatch(path) for path in paths):
            continue
        changed = changed_capability_ids(
            root,
            item,
            reporter,
            repo=repo,
            token=token,
            base_sha=base_sha,
        )
        undeclared = sorted(changed - capabilities)
        if undeclared:
            reporter.error(
                "PR-CAPABILITY-SCOPE-001",
                f"changed Capability IDs are not declared in capabilities: {', '.join(undeclared)}",
                item.get("filename"),
            )


def validate_declared_scope(
    root: Path,
    body: str,
    changed_files: list[dict] | list[str],
    reporter: Reporter,
    *,
    repo: str | None = None,
    token: str | None = None,
    base_sha: str | None = None,
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

    for entry in changed_file_entries(changed_files):
        path = entry["path"]
        path_change_id = core.change_id_from_path(path)
        if path_change_id is not None:
            if path_change_id not in change_ids:
                reporter.error(
                    "PR-SCOPE-001",
                    f"changed Change asset {path} is not declared in the PR body",
                    path,
                )
            continue
        required = required_change_types(
            root,
            path,
            reporter,
            entry=entry,
            repo=repo,
            token=token,
            base_sha=base_sha,
        )
        if required and not (declared_types & required):
            reporter.error(
                "PR-SCOPE-002",
                f"file requires one of Change types {sorted(required)}, declared types are {sorted(declared_types)}",
                path,
            )

    validate_exact_asset_scope(
        root,
        changed_files,
        metadata,
        reporter,
        repo=repo,
        token=token,
        base_sha=base_sha,
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
