#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
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
        parse_time(comment["created_at"])
        for comment in comments
        if normalized_login(comment.get("user", {}).get("login")) == author
        and pattern.search(comment.get("body") or "")
    ]
    return max(matching) if matching else None


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    number_text = os.getenv("PR_NUMBER")
    expected_head = os.getenv("PR_HEAD_SHA")
    if not all((token, repo, number_text, expected_head)):
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
        if current_head != expected_head:
            print(f"PR head SHA mismatch: event={expected_head}, current={current_head}.")
            return 1

        rule = config.get("review", {})
        actors = {normalized_login(value) for value in rule.get("actors", [])}
        accepted_states = set(rule.get("accepted_states", []))
        author = normalized_login(pull_request.get("user", {}).get("login"))

        reviews = rest_pages(f"https://api.github.com/repos/{repo}/pulls/{number}/reviews", token)
        current_reviews = [
            review
            for review in reviews
            if normalized_login(review.get("user", {}).get("login")) in actors
            and normalized_login(review.get("user", {}).get("login")) != author
            and review.get("commit_id") == current_head
        ]
        if any(review.get("state") == "CHANGES_REQUESTED" for review in current_reviews):
            print("Current head has requested changes.")
            return 1
        accepted = any(review.get("state") in accepted_states for review in current_reviews)

        if not accepted and rule.get("accept_positive_reaction"):
            request_time = latest_head_review_request(repo, number, token, author, current_head)
            if request_time is not None:
                reactions = rest_pages(
                    f"https://api.github.com/repos/{repo}/issues/{number}/reactions",
                    token,
                )
                accepted = any(
                    reaction.get("content") == "+1"
                    and normalized_login(reaction.get("user", {}).get("login")) in actors
                    and normalized_login(reaction.get("user", {}).get("login")) != author
                    and parse_time(reaction["created_at"]) >= request_time
                    for reaction in reactions
                )

        if not accepted:
            print(
                "No configured independent review for the current head. "
                f"For a reaction-only Codex review, comment exactly: @codex review {current_head}"
            )
            return 1

        if rule.get("require_resolved_threads"):
            threads = unresolved_threads(repo, number, token)
            if threads:
                print(f"{len(threads)} unresolved current review thread(s) remain.")
                return 1

        print("PR governance passed.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, urllib.error.URLError) as exc:
        print(f"PR governance failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
