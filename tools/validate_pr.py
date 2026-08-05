#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATUS_CONTEXT = "pr-governance"
CHANGE_ID_PATTERN = re.compile(r"\bCHG-\d{4}\b")
CHANGE_DECLARATION_PATTERN = re.compile(r"(?im)^-\s*Change IDs?\s*[:：]\s*(.+?)\s*$")
CHANGE_PATH_PATTERN = re.compile(r"^changes/(CHG-\d{4})-[^/]+/change\.yaml$")


def api(url: str, token: str, method: str = "GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
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


def normalized_login(value: str | None) -> str:
    return (value or "").removesuffix("[bot]")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def status_target_url() -> str | None:
    server = os.getenv("GITHUB_SERVER_URL")
    repository = os.getenv("GITHUB_REPOSITORY")
    run_id = os.getenv("GITHUB_RUN_ID")
    if server and repository and run_id:
        return f"{server}/{repository}/actions/runs/{run_id}"
    return None


def publish_status(
    repo: str,
    head_sha: str,
    token: str,
    state: str,
    description: str,
) -> None:
    payload = {
        "state": state,
        "context": STATUS_CONTEXT,
        "description": description[:140],
    }
    target_url = status_target_url()
    if target_url:
        payload["target_url"] = target_url
    api(
        f"https://api.github.com/repos/{repo}/statuses/{head_sha}",
        token,
        "POST",
        payload,
    )


def latest_reviews_by_actor(reviews: list[dict]) -> list[dict]:
    latest: dict[str, tuple[tuple[datetime, int], dict]] = {}
    for review in reviews:
        actor = normalized_login(review.get("user", {}).get("login"))
        submitted_at = review.get("submitted_at")
        if not actor or not isinstance(submitted_at, str):
            continue
        order = (parse_time(submitted_at), int(review.get("id") or 0))
        if actor not in latest or order > latest[actor][0]:
            latest[actor] = (order, review)
    return [entry[1] for entry in latest.values()]


def unresolved_threads(repo: str, number: int, token: str) -> list[dict]:
    owner, name = repo.split("/", 1)
    query = """
    query($owner:String!,$name:String!,$number:Int!,$after:String){
      repository(owner:$owner,name:$name){
        pullRequest(number:$number){
          reviewThreads(first:100,after:$after){
            nodes{isResolved isOutdated}
            pageInfo{hasNextPage endCursor}
          }
        }
      }
    }
    """
    after = None
    result: list[dict] = []
    while True:
        payload = api(
            "https://api.github.com/graphql",
            token,
            "POST",
            {
                "query": query,
                "variables": {
                    "owner": owner,
                    "name": name,
                    "number": number,
                    "after": after,
                },
            },
        )
        threads = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        result.extend(
            thread
            for thread in threads["nodes"]
            if not thread["isResolved"] and not thread["isOutdated"]
        )
        page_info = threads["pageInfo"]
        if not page_info["hasNextPage"]:
            return result
        after = page_info["endCursor"]


def latest_head_review_request(
    repo: str,
    number: int,
    token: str,
    author: str,
    head_sha: str,
) -> tuple[int, datetime] | None:
    pattern = re.compile(rf"(?im)^@codex\s+review\s+{re.escape(head_sha)}\s*$")
    comments = rest_pages(f"https://api.github.com/repos/{repo}/issues/{number}/comments", token)
    matching: list[tuple[datetime, int]] = []
    for comment in comments:
        if normalized_login(comment.get("user", {}).get("login")) != author:
            continue
        if not pattern.search(comment.get("body") or ""):
            continue
        boundary = parse_time(comment.get("updated_at") or comment["created_at"])
        matching.append((boundary, int(comment["id"])))
    if not matching:
        return None
    boundary, comment_id = max(matching)
    return comment_id, boundary


def has_positive_reaction(
    repo: str,
    number: int,
    token: str,
    command_comment_id: int,
    boundary: datetime,
    actors: set[str],
    author: str,
) -> bool:
    comment_reactions = rest_pages(
        f"https://api.github.com/repos/{repo}/issues/comments/{command_comment_id}/reactions",
        token,
    )
    issue_reactions = rest_pages(
        f"https://api.github.com/repos/{repo}/issues/{number}/reactions",
        token,
    )
    return any(
        reaction.get("content") == "+1"
        and normalized_login(reaction.get("user", {}).get("login")) in actors
        and normalized_login(reaction.get("user", {}).get("login")) != author
        and parse_time(reaction["created_at"]) >= boundary
        for reaction in comment_reactions + issue_reactions
    )


def review_evidence(
    repo: str,
    number: int,
    token: str,
    current_head: str,
    author: str,
    rule: dict,
) -> tuple[bool, str]:
    actors = {normalized_login(value) for value in rule.get("actors", [])}
    accepted_states = set(rule.get("accepted_states", []))
    reviews = rest_pages(f"https://api.github.com/repos/{repo}/pulls/{number}/reviews", token)
    current_reviews = [
        review
        for review in reviews
        if normalized_login(review.get("user", {}).get("login")) in actors
        and normalized_login(review.get("user", {}).get("login")) != author
        and review.get("commit_id") == current_head
    ]
    latest_reviews = latest_reviews_by_actor(current_reviews)
    if any(review.get("state") == "CHANGES_REQUESTED" for review in latest_reviews):
        return False, "A configured reviewer currently requests changes on the current head."
    if any(review.get("state") in accepted_states for review in latest_reviews):
        return True, "Current-head review submission found."

    if rule.get("accept_positive_reaction"):
        request = latest_head_review_request(repo, number, token, author, current_head)
        if request is not None:
            command_comment_id, boundary = request
            if has_positive_reaction(
                repo,
                number,
                token,
                command_comment_id,
                boundary,
                actors,
                author,
            ):
                return True, "Head-bound positive review reaction found."
    return False, "No configured independent review for the current head."


def extract_change_ids(body: str) -> set[str]:
    result: set[str] = set()
    for declaration in CHANGE_DECLARATION_PATTERN.findall(body or ""):
        result.update(CHANGE_ID_PATTERN.findall(declaration))
    return result


def decode_contents(payload: object) -> str:
    if not isinstance(payload, dict) or payload.get("encoding") != "base64":
        raise TypeError("GitHub contents response must contain base64 content")
    content = payload.get("content")
    if not isinstance(content, str):
        raise TypeError("GitHub contents response has no content")
    return base64.b64decode(content).decode("utf-8")


def change_paths(repo: str, number: int, token: str, change_ids: set[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in rest_pages(f"https://api.github.com/repos/{repo}/pulls/{number}/files", token):
        path = item.get("filename")
        match = CHANGE_PATH_PATTERN.fullmatch(path) if isinstance(path, str) else None
        if match and match.group(1) in change_ids:
            result[match.group(1)] = path
    for change_id in change_ids - set(result):
        matches = sorted((ROOT / "changes").glob(f"{change_id}-*/change.yaml"))
        if len(matches) == 1:
            result[change_id] = str(matches[0].relative_to(ROOT))
    return result


def change_profiles(
    repo: str,
    number: int,
    token: str,
    head_sha: str,
    body: str,
) -> dict[str, str]:
    change_ids = extract_change_ids(body)
    if not change_ids:
        raise ValueError("PR body must declare at least one Change")
    paths = change_paths(repo, number, token, change_ids)
    missing = sorted(change_ids - set(paths))
    if missing:
        raise ValueError(f"cannot resolve Change metadata for: {', '.join(missing)}")
    result: dict[str, str] = {}
    for change_id, path in paths.items():
        payload = api(
            f"https://api.github.com/repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(head_sha, safe='')}",
            token,
        )
        value = yaml.safe_load(decode_contents(payload))
        profile = value.get("change_profile") if isinstance(value, dict) else None
        if not isinstance(profile, str):
            raise ValueError(f"{change_id} has no valid change_profile")
        result[change_id] = profile
    return result


def is_human_review(review: dict, author: str, ai_actors: set[str]) -> bool:
    user = review.get("user") if isinstance(review, dict) else None
    login = normalized_login(user.get("login") if isinstance(user, dict) else None)
    user_type = user.get("type") if isinstance(user, dict) else None
    return bool(login) and login != author and login not in ai_actors and user_type != "Bot"


def has_current_head_human_approval(
    reviews: list[dict],
    current_head: str,
    author: str,
    ai_actors: set[str],
) -> bool:
    current = [
        review
        for review in reviews
        if review.get("commit_id") == current_head and is_human_review(review, author, ai_actors)
    ]
    return any(review.get("state") == "APPROVED" for review in latest_reviews_by_actor(current))


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    number_text = os.getenv("PR_NUMBER")
    expected_head = os.getenv("PR_HEAD_SHA")
    comment_body = (os.getenv("GITHUB_COMMENT_BODY") or "").strip()
    wait_seconds = max(0, int(os.getenv("WAIT_FOR_REACTION_SECONDS", "0")))
    poll_seconds = max(1, int(os.getenv("REVIEW_POLL_SECONDS", "10")))
    if not all((token, repo, number_text)):
        print("PR governance skipped outside pull request.")
        return 0

    current_head: str | None = None
    try:
        number = int(number_text)
        config = yaml.safe_load((ROOT / ".github/governance.yaml").read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            print(".github/governance.yaml must contain an object.")
            return 1

        pull_request = api(f"https://api.github.com/repos/{repo}/pulls/{number}", token)
        current_head = pull_request["head"]["sha"]
        if expected_head and current_head != expected_head:
            publish_status(repo, current_head, token, "failure", "PR head SHA mismatch")
            print(f"PR head SHA mismatch: event={expected_head}, current={current_head}.")
            return 1

        if number in config.get("bootstrap_pull_requests", []):
            publish_status(repo, current_head, token, "success", "Explicit bootstrap exception")
            print(f"PR #{number} is an explicit bootstrap exception.")
            return 0

        publish_status(repo, current_head, token, "pending", "Waiting for current-head review evidence")
        author = normalized_login(pull_request.get("user", {}).get("login"))
        exact_command = f"@codex review {current_head}"
        should_wait = comment_body == exact_command and wait_seconds > 0
        deadline = time.monotonic() + wait_seconds if should_wait else time.monotonic()

        while True:
            accepted, reason = review_evidence(
                repo,
                number,
                token,
                current_head,
                author,
                config.get("review", {}),
            )
            if accepted:
                break
            if time.monotonic() >= deadline:
                publish_status(repo, current_head, token, "failure", "Missing current-head review evidence")
                print(reason)
                print(f"Trigger a reaction-only review with the exact command: {exact_command}")
                return 1
            time.sleep(poll_seconds)

        profiles = change_profiles(
            repo,
            number,
            token,
            current_head,
            pull_request.get("body") or "",
        )
        high_risk = sorted(
            change_id for change_id, profile in profiles.items() if profile == "high-risk"
        )
        high_risk_rule = config.get("high_risk", {})
        if high_risk and high_risk_rule.get("require_human_approval", True):
            reviews = rest_pages(f"https://api.github.com/repos/{repo}/pulls/{number}/reviews", token)
            ai_actors = {
                normalized_login(value)
                for value in config.get("review", {}).get("actors", [])
            }
            if not has_current_head_human_approval(reviews, current_head, author, ai_actors):
                publish_status(repo, current_head, token, "failure", "High-risk Change needs human approval")
                print(
                    "High-risk Change(s) require a non-author human APPROVED review on the current head: "
                    + ", ".join(high_risk)
                )
                return 1

        if config.get("review", {}).get("require_resolved_threads"):
            threads = unresolved_threads(repo, number, token)
            if threads:
                publish_status(repo, current_head, token, "failure", "Unresolved review threads remain")
                print(f"{len(threads)} unresolved current review thread(s) remain.")
                return 1

        publish_status(repo, current_head, token, "success", reason)
        print("PR governance passed: " + reason)
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, urllib.error.URLError) as exc:
        if current_head and token and repo:
            try:
                publish_status(repo, current_head, token, "failure", "PR governance execution failed")
            except Exception:
                pass
        print(f"PR governance failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
