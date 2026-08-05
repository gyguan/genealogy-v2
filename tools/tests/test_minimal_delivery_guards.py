from __future__ import annotations

import sys
import unittest
from pathlib import Path

try:
    from .validation_test_utils import copy_repo
except ImportError:
    from validation_test_utils import copy_repo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from diagnostics import Reporter  # noqa: E402
from run_change_tests import safe_environment, validated_argv  # noqa: E402
from validate_change_quality_strict import placeholder_identifier  # noqa: E402
from validate_pr import has_current_head_human_approval  # noqa: E402
from validate_pr_change_strict import validate_exact_asset_scope  # noqa: E402


def capability_file(*items: tuple[str, str]) -> str:
    rows = "\n".join(
        f"  - id: {capability_id}\n    name: {name}"
        for capability_id, name in items
    )
    return f"version: 1\ngroup:\n  id: CAP-GROUP-TEST\n  capabilities:\n{rows}\n"


class RegisteredTestCommandTests(unittest.TestCase):
    def test_python_command_is_allowed_without_shell(self) -> None:
        self.assertEqual(
            ["python", "-m", "unittest", "tools.tests.test_minimal_delivery_guards"],
            validated_argv(
                "python -m unittest tools.tests.test_minimal_delivery_guards"
            ),
        )

    def test_shell_operators_and_arbitrary_paths_are_rejected(self) -> None:
        for command in (
            "python -m unittest && curl example.test",
            "/tmp/python -m unittest",
            "bash -c true",
            "python -m unittest > result.txt",
        ):
            with self.subTest(command=command):
                with self.assertRaises(ValueError):
                    validated_argv(command)

    def test_test_process_environment_does_not_receive_tokens(self) -> None:
        env = safe_environment(
            {
                "PATH": "/usr/bin",
                "HOME": "/tmp/home",
                "GITHUB_TOKEN": "secret",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "oidc",
                "CUSTOM_SECRET": "hidden",
            }
        )
        self.assertEqual({"PATH": "/usr/bin", "HOME": "/tmp/home"}, env)

    def test_workflow_does_not_give_token_to_registered_test_parent(self) -> None:
        text = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        marker = "- run: python tools/run_change_tests.py"
        self.assertIn(marker, text)
        block = text.split(marker, 1)[1].split("\n      - ", 1)[0]
        self.assertIn("PR_BODY:", block)
        self.assertNotIn("GITHUB_TOKEN", block)


class ExactAffectedScopeTests(unittest.TestCase):
    def metadata(self, **values):
        base = {
            "affected_domains": [],
            "affected_decisions": [],
            "capabilities": [],
        }
        base.update(values)
        return {"CHG-9999": base}

    def test_changed_domain_must_be_declared(self) -> None:
        reporter = Reporter()
        validate_exact_asset_scope(
            ROOT,
            ["domains/person-registry.md"],
            self.metadata(),
            reporter,
            repo=None,
            token=None,
            base_sha=None,
        )
        self.assertTrue(any(item.code == "PR-DOMAIN-SCOPE-001" for item in reporter.errors))

    def test_changed_decision_must_be_declared(self) -> None:
        reporter = Reporter()
        validate_exact_asset_scope(
            ROOT,
            ["decisions/DEC-0001-module-boundaries.md"],
            self.metadata(),
            reporter,
            repo=None,
            token=None,
            base_sha=None,
        )
        self.assertTrue(any(item.code == "PR-DECISION-SCOPE-001" for item in reporter.errors))

    def test_only_modified_capability_ids_need_declaration(self) -> None:
        root = copy_repo(self)
        path = root / "product/capabilities/test-scope.yaml"
        path.write_text(
            capability_file(("CAP-TEST-001", "changed"), ("CAP-TEST-002", "stable")),
            encoding="utf-8",
        )
        files = [
            {
                "filename": "product/capabilities/test-scope.yaml",
                "status": "modified",
                "base_content": capability_file(
                    ("CAP-TEST-001", "old"),
                    ("CAP-TEST-002", "stable"),
                ),
            }
        ]
        reporter = Reporter()
        validate_exact_asset_scope(
            root,
            files,
            self.metadata(capabilities=["CAP-TEST-001"]),
            reporter,
            repo=None,
            token=None,
            base_sha=None,
        )
        self.assertFalse(reporter.errors, reporter.render("test"))

        reporter = Reporter()
        validate_exact_asset_scope(
            root,
            files,
            self.metadata(capabilities=[]),
            reporter,
            repo=None,
            token=None,
            base_sha=None,
        )
        errors = [item for item in reporter.errors if item.code == "PR-CAPABILITY-SCOPE-001"]
        self.assertEqual(1, len(errors))
        self.assertIn("CAP-TEST-001", errors[0].message)
        self.assertNotIn("CAP-TEST-002", errors[0].message)


class PlaceholderIdentifierTests(unittest.TestCase):
    def test_template_identifiers_are_rejected(self) -> None:
        for value in (
            "SPEC-REPLACE-ME",
            "SCN-EXAMPLE-01",
            "TASK-SAMPLE-001",
            "TEST-TEMPLATE-001",
            "RULE-PLACEHOLDER-001",
            "MODULE-XXXX-001",
            "SEC-0000-001",
        ):
            with self.subTest(value=value):
                self.assertTrue(placeholder_identifier(value))
        self.assertFalse(placeholder_identifier("SPEC-GOV-GUARD-001"))


class HighRiskHumanApprovalTests(unittest.TestCase):
    def review(self, login: str, state: str, review_id: int, *, user_type: str = "User"):
        return {
            "id": review_id,
            "state": state,
            "commit_id": "head-sha",
            "submitted_at": f"2026-08-05T04:{review_id:02d}:00Z",
            "user": {"login": login, "type": user_type},
        }

    def test_bot_or_author_does_not_satisfy_high_risk_approval(self) -> None:
        reviews = [
            self.review("chatgpt-codex-connector[bot]", "APPROVED", 1, user_type="Bot"),
            self.review("author", "APPROVED", 2),
        ]
        self.assertFalse(
            has_current_head_human_approval(
                reviews,
                "head-sha",
                "author",
                {"chatgpt-codex-connector"},
            )
        )

    def test_latest_human_approval_satisfies_high_risk_policy(self) -> None:
        reviews = [self.review("reviewer", "APPROVED", 3)]
        self.assertTrue(
            has_current_head_human_approval(
                reviews,
                "head-sha",
                "author",
                {"chatgpt-codex-connector"},
            )
        )

    def test_later_comment_does_not_invalidate_human_approval(self) -> None:
        reviews = [
            self.review("reviewer", "APPROVED", 3),
            self.review("reviewer", "COMMENTED", 4),
        ]
        self.assertTrue(
            has_current_head_human_approval(
                reviews,
                "head-sha",
                "author",
                {"chatgpt-codex-connector"},
            )
        )

    def test_later_changes_requested_invalidates_human_approval(self) -> None:
        reviews = [
            self.review("reviewer", "APPROVED", 3),
            self.review("reviewer", "CHANGES_REQUESTED", 4),
        ]
        self.assertFalse(
            has_current_head_human_approval(
                reviews,
                "head-sha",
                "author",
                {"chatgpt-codex-connector"},
            )
        )

    def test_pr_body_edit_revalidates_profile_governance(self) -> None:
        text = (ROOT / ".github/workflows/pr-governance.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("pull_request:\n    types: [edited]", text)
        self.assertIn("github.event_name == 'pull_request'", text)


if __name__ == "__main__":
    unittest.main()
