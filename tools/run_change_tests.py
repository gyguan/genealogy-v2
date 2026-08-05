#!/usr/bin/env python3
from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Iterable

import yaml

import validate_pr_change as pr_change

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT_SECONDS = 300
ALLOWED_RUNNERS = {
    "python",
    "python3",
    "pytest",
    "npm",
    "npx",
    "mvn",
    "gradle",
}
ALLOWED_WRAPPERS = {"./mvnw", "./gradlew"}
SHELL_OPERATORS = {"|", "||", "&&", ";", ">", ">>", "<", "<<", "2>", "2>>"}
SAFE_ENVIRONMENT_KEYS = {
    "PATH",
    "HOME",
    "CI",
    "LANG",
    "LC_ALL",
    "JAVA_HOME",
    "M2_HOME",
    "GRADLE_HOME",
    "NODE_OPTIONS",
    "PYTHONPATH",
    "RUNNER_TEMP",
    "TMPDIR",
    "TEMP",
    "TMP",
}


def resolve_change(root: Path, change_id: str) -> Path:
    matches = sorted((root / "changes").glob(f"{change_id}-*"))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one repository Change for {change_id}")
    return matches[0]


def validated_argv(command: str) -> list[str]:
    if not isinstance(command, str) or not command.strip():
        raise ValueError("registered test command must be a non-empty string")
    if "\n" in command or "\r" in command:
        raise ValueError("registered test command must be a single line")
    argv = shlex.split(command, posix=True)
    if not argv:
        raise ValueError("registered test command has no executable")
    executable = argv[0].replace("\\", "/")
    if "/" in executable:
        if executable not in ALLOWED_WRAPPERS:
            raise ValueError(f"registered test executable path {executable!r} is not allowed")
    elif executable not in ALLOWED_RUNNERS:
        raise ValueError(f"registered test runner {executable!r} is not allowed")
    for token in argv:
        if token in SHELL_OPERATORS or "$(" in token or "`" in token:
            raise ValueError("registered test command contains a shell operator")
        if token.startswith((">", "<")):
            raise ValueError("registered test command contains redirection")
    return argv


def registered_commands(change_dir: Path) -> list[tuple[str, list[str]]]:
    path = change_dir / "tests.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read {path.relative_to(ROOT)}: {exc}") from exc
    tests = data.get("tests") if isinstance(data, dict) else None
    if not isinstance(tests, list) or not tests:
        raise ValueError(f"{path.relative_to(ROOT)} must register at least one test")

    result: list[tuple[str, list[str]]] = []
    for index, item in enumerate(tests):
        if not isinstance(item, dict):
            raise ValueError(f"{path.relative_to(ROOT)} tests[{index}] must be an object")
        test_id = item.get("id")
        if not isinstance(test_id, str) or not test_id:
            raise ValueError(f"{path.relative_to(ROOT)} tests[{index}] needs id")
        result.append((test_id, validated_argv(item.get("command"))))
    return result


def collect_commands(root: Path, change_ids: Iterable[str]) -> list[tuple[str, str, list[str]]]:
    result: list[tuple[str, str, list[str]]] = []
    seen: set[tuple[str, ...]] = set()
    for change_id in sorted(set(change_ids)):
        for test_id, argv in registered_commands(resolve_change(root, change_id)):
            key = tuple(argv)
            if key in seen:
                continue
            seen.add(key)
            result.append((change_id, test_id, argv))
    return result


def safe_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    values = dict(os.environ) if source is None else source
    return {key: value for key, value in values.items() if key in SAFE_ENVIRONMENT_KEYS}


def execute_commands(
    commands: Iterable[tuple[str, str, list[str]]],
    *,
    root: Path = ROOT,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    environment: dict[str, str] | None = None,
) -> list[str]:
    failures: list[str] = []
    env = safe_environment(environment)
    for change_id, test_id, argv in commands:
        rendered = shlex.join(argv)
        print(f"==> {change_id} {test_id}: {rendered}", flush=True)
        try:
            result = subprocess.run(
                argv,
                cwd=root,
                check=False,
                timeout=timeout_seconds,
                env=env,
            )
        except subprocess.TimeoutExpired:
            failures.append(f"{change_id}/{test_id}: timed out after {timeout_seconds}s")
            continue
        except OSError as exc:
            failures.append(f"{change_id}/{test_id}: cannot execute: {exc}")
            continue
        if result.returncode:
            failures.append(f"{change_id}/{test_id}: exit code {result.returncode}")
    return failures


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    number_text = os.getenv("PR_NUMBER")
    if not all((token, repo, number_text)):
        print("Registered Change tests skipped outside pull request.")
        return 0

    try:
        number = int(number_text)
        pull_request = pr_change.api(f"https://api.github.com/repos/{repo}/pulls/{number}", token)
        change_ids = pr_change.extract_change_ids(pull_request.get("body") or "")
        if not change_ids:
            raise ValueError("PR body must declare at least one Change before tests can run")
        timeout_seconds = max(
            1,
            int(os.getenv("CHANGE_TEST_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))),
        )
        failures = execute_commands(
            collect_commands(ROOT, change_ids),
            timeout_seconds=timeout_seconds,
        )
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"Registered Change tests failed to start: {exc}")
        return 1

    if failures:
        print("Registered Change tests failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Registered Change tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
