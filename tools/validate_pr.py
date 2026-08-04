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
                "variables": {"owner": owner, "name": name, "number": number, "after": after},
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
) -> datetime | None:
    pattern = re.compile(rf"(?im)^@codex\s+review\s+{re.escape(head_sha)}\s*$")
    comments = rest_pages(f"https://api.github.com/repos/{repo}/issues/{number}/comments", token)
    matching = [
        parse_time(comment.get("updated_at") or comment["created_at"])
        for comment in comments
        if normalized_login(comment.get("user", {}).get("login")) == author
        and pattern.search(comment.get("body") or "")
    ]
    return max(matching) if matching else None


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
        request_time = latest_head_review_request(repo, number, token, author, current_head)
        if request_time is not None:
            reactions = rest_pages(
                f"https://api.github.com/repos/{repo}/issues/{number}/reactions",
                token,
            )
            if any(
                reaction.get("content") == "+1"
                and normalized_login(reaction.get("user", {}).get("login")) in actors
                and normalized_login(reaction.get("user", {}).get("login")) != author
                and parse_time(reaction["created_at"]) >= request_time
                for reaction in reactions
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

    try:
        number = int(number_text)
        config = yaml.safe_load((ROOT / ".github/governance.yaml").read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            print(".github/governance.yaml must contain an object.")
            return 1
        if number in config.get("bootstrap_pull_requests", []):
            print(f"PR #{number} is an explicit bootstrap exception.")
            return 0

        pull_request = api(f"https://api.github.com/repos/{repo}/pulls/{number}", token)
        current_head = pull_request["head"]["sha"]
        if expected_head and current_head != expected_head:
            print(f"PR head SHA mismatch: event={expected_head}, current={current_head}.")
            return 1

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
                print(reason)
                print(f"Trigger a reaction-only review with the exact command: {exact_command}")
                return 1
            time.sleep(poll_seconds)

        if config.get("review", {}).get("require_resolved_threads"):
            threads = unresolved_threads(repo, number, token)
            if threads:
                print(f"{len(threads)} unresolved current review thread(s) remain.")
                return 1

        print("PR governance passed: " + reason)
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, urllib.error.URLError) as exc:
        print(f"PR governance failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
