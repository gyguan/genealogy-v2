from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PullRequestGovernanceWorkflowTests(unittest.TestCase):
    def workflow_text(self) -> str:
        return (ROOT / ".github/workflows/pr-governance.yml").read_text(
            encoding="utf-8"
        )

    def test_review_changes_use_writable_workflow_run_context(self) -> None:
        text = self.workflow_text()
        self.assertIn(
            "workflow_run:\n    workflows: [Repository Validation]\n    types: [completed]",
            text,
        )
        self.assertIn("github.event_name == 'workflow_run'", text)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", text)
        self.assertIn("github.event.workflow_run.pull_requests[0] != null", text)
        self.assertNotIn("pull_request_review:", text)

    def test_writable_rerun_executes_only_default_branch_governance_code(self) -> None:
        text = self.workflow_text()
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn(
            "github.event.workflow_run.pull_requests[0].number",
            text,
        )
        self.assertIn(
            "github.event.workflow_run.pull_requests[0].head.sha",
            text,
        )
        self.assertNotIn("download-artifact", text)
        self.assertNotIn("github.event.workflow_run.head_branch", text)


if __name__ == "__main__":
    unittest.main()
