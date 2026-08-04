from __future__ import annotations

import os
import subprocess
import sys
import unittest

from validation_test_utils import ROOT, copy_repo

sys.path.insert(0, str(ROOT / "tools"))
from validate_pr import latest_reviews_by_actor  # noqa: E402


class ToolTests(unittest.TestCase):
    def test_new_change_and_context(self) -> None:
        root = copy_repo(self)
        created = subprocess.run(
            [
                sys.executable,
                "tools/new_change.py",
                "CHG-0099",
                "sample",
                "--type",
                "engineering",
                "--issue",
                "99",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        context = subprocess.run(
            [sys.executable, "tools/context.py", "CHG-0099"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, context.returncode, context.stdout + context.stderr)
        self.assertIn("CHG-0099-sample/change.yaml", context.stdout)

    def test_pr_validation_skips_outside_pull_request(self) -> None:
        environment = os.environ.copy()
        for name in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER", "PR_HEAD_SHA"):
            environment.pop(name, None)
        result = subprocess.run(
            [sys.executable, "tools/validate_pr.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, result.returncode)
        self.assertIn("skipped", result.stdout)

    def test_latest_review_state_wins_per_actor(self) -> None:
        reviews = [
            {
                "id": 1,
                "state": "CHANGES_REQUESTED",
                "submitted_at": "2026-08-04T01:00:00Z",
                "user": {"login": "reviewer[bot]"},
            },
            {
                "id": 2,
                "state": "COMMENTED",
                "submitted_at": "2026-08-04T01:01:00Z",
                "user": {"login": "reviewer[bot]"},
            },
        ]
        latest = latest_reviews_by_actor(reviews)
        self.assertEqual(1, len(latest))
        self.assertEqual("COMMENTED", latest[0]["state"])


if __name__ == "__main__":
    unittest.main()
