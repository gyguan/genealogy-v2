#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STATUS_CONTEXT = "pr-governance"


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
