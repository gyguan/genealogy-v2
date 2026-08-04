#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

import yaml

from diagnostics import Reporter

ROOT = Path(__file__).resolve().parents[1]
CHANGE_ID_PATTERN = re.compile(r"\bCHG-\d{4}\b")
CHANGE_DECLARATION_PATTERN = re.compile(r"(?im)^-\s*Change IDs?\s*[:：]\s*(.+?)\s*$")
DECISION_CHANGE_TYPES = {"product", "domain", "engineering", "governance", "security"}


def api(url: str, token: str):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def rest_pages(url: str, token: str) -> list[dict]:
    separator = "&" if "?" in url else "?"
    result: list[dict] = []
    page = 1
    while True:
        values = api(f"{url}{separator}per_page=100&page={page}", token)
        if not isinstance(values, list):
            raise TypeError(f"Expected a list from {url}")
        result.extend(values)
        if len(values) < 100:
            return result
        page += 1


def extract_change_ids(body: str) -> set[str]:
    result: set[str] = set()
    for declaration in CHANGE_DECLARATION_PATTERN.findall(body or ""):
        result.update(CHANGE_ID_PATTERN.findall(declaration))
    return result


def changed_file_paths(files: list[dict]) -> list[str]:
    paths: list[str] = []
    for item in files:
        filename = item.get("filename")
        if isinstance(filename, str):
            paths.append(filename)
        if item.get("status") == "renamed":
            previous = item.get("previous_filename")
            if isinstance(previous, str):
                paths.append(previous)
    return list(dict.fromkeys(paths))


def resolve_change(root: Path, change_id: str) -> Path | None:
    matches = sorted((root / "changes").glob(f"{change_id}-*"))
    return matches[0] if len(matches) == 1 else None


def required_change_types(path: str) -> set[str]:
    if path.startswith("product/"):
        return {"product"}
    if path.startswith("domains/"):
        return {"domain"}
    if path.startswith("decisions/"):
        return set(DECISION_CHANGE_TYPES)
    if path == "SECURITY.md":
        return {"security", "governance"}
    if (
        path.startswith("tools/")
        or path.startswith(".github/")
        or path.startswith("skills/")
        or path.startswith("changes/_template/")
        or path in {"AGENTS.md", "README.md", "changes/README.md"}
    ):
        return {"governance", "engineering"}
    return {"engineering", "domain", "security"}


def change_id_from_path(path: str) -> str | None:
    match = re.match(r"^changes/(CHG-\d{4})-[^/]+/", path)
    return match.group(1) if match else None


def load_change_metadata(root: Path, change_id: str, reporter: Reporter) -> dict:
    directory = resolve_change(root, change_id)
    if directory is None:
        reporter.error("PR-CHANGE-001", f"expected exactly one repository Change for {change_id}")
        return {}
    path = directory / "change.yaml"
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        reporter.error("PR-CHANGE-002", f"cannot read {change_id}: {exc}", str(path.relative_to(root)))
        return {}
    if not isinstance(value, dict):
        reporter.error("PR-CHANGE-003", f"{change_id} metadata must be an object", str(path.relative_to(root)))
        return {}
    return value


def validate_declared_scope(
    root: Path,
    body: str,
    changed_files: list[str],
    reporter: Reporter,
) -> dict[str, dict]:
    change_ids = extract_change_ids(body)
    if not change_ids:
        reporter.error(
            "PR-BODY-001",
            "PR body must declare at least one Change using '- Change ID：CHG-xxxx'",
        )
        return {}

    metadata = {
        change_id: load_change_metadata(root, change_id, reporter)
        for change_id in sorted(change_ids)
    }
    declared_types = {
        value.get("change_type")
        for value in metadata.values()
        if isinstance(value.get("change_type"), str)
    }

    for path in changed_files:
        path_change_id = change_id_from_path(path)
        if path_change_id is not None:
            if path_change_id not in change_ids:
                reporter.error(
                    "PR-SCOPE-001",
                    f"changed Change asset {path} is not declared in the PR body",
                    path,
                )
            continue
        required = required_change_types(path)
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


def validate_issues(repo: str, token: str, metadata: dict[str, dict], reporter: Reporter) -> None:
    for change_id, value in metadata.items():
        issue = value.get("issue")
        number = issue.get("number") if isinstance(issue, dict) else None
        repository = issue.get("repository") if isinstance(issue, dict) else None
        if not isinstance(number, int) or number <= 0:
            reporter.error("PR-ISSUE-001", f"{change_id} needs a real GitHub Issue number")
            continue
        if repository != repo:
            reporter.error("PR-ISSUE-002", f"{change_id} issue repository must be {repo}")
            continue
        issue_data = api(f"https://api.github.com/repos/{repo}/issues/{number}", token)
        if issue_data.get("pull_request") is not None:
            reporter.error("PR-ISSUE-003", f"{change_id} references PR #{number} instead of an Issue")


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    number_text = os.getenv("PR_NUMBER")
    if not all((token, repo, number_text)):
        print("PR Change validation skipped outside pull request.")
        return 0

    reporter = Reporter()
    try:
        number = int(number_text)
        pull_request = api(f"https://api.github.com/repos/{repo}/pulls/{number}", token)
        files = rest_pages(f"https://api.github.com/repos/{repo}/pulls/{number}/files", token)
        metadata = validate_declared_scope(
            ROOT,
            pull_request.get("body") or "",
            changed_file_paths(files),
            reporter,
        )
        validate_issues(repo, token, metadata, reporter)
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError, urllib.error.URLError) as exc:
        reporter.error("PR-EXEC-001", f"PR Change validation failed to execute: {exc}")

    print(reporter.render("PR Change validation"))
    return reporter.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
