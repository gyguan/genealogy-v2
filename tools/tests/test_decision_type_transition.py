from __future__ import annotations

import sys
import unittest

import yaml

try:
    from .validation_test_utils import ROOT, copy_repo
except ImportError:
    from validation_test_utils import ROOT, copy_repo

sys.path.insert(0, str(ROOT / "tools"))

from diagnostics import Reporter  # noqa: E402
from validate_pr_change_strict import validate_declared_scope  # noqa: E402


def decision_text(decision_id: str, decision_type: str) -> str:
    return (
        "---\n"
        f"id: {decision_id}\n"
        f"type: {decision_type}\n"
        "status: accepted\n"
        "affected_domains: []\n"
        "introduced_by: CHG-0004\n"
        "supersedes: []\n"
        "effective_at: 2026-08-05\n"
        "---\n\n"
        "# Decision\n"
    )


class ModifiedDecisionTypeTransitionTests(unittest.TestCase):
    def test_base_and_head_decision_types_are_both_required(self) -> None:
        root = copy_repo(self)
        change_dir = root / "changes/CHG-9999-decision-transition"
        change_dir.mkdir()
        (change_dir / "change.yaml").write_text(
            yaml.safe_dump(
                {
                    "version": 2,
                    "id": "CHG-9999",
                    "title": "decision-transition",
                    "change_type": "engineering",
                    "change_profile": "standard",
                    "quality_policy": "strict",
                    "status": "implementing",
                    "capabilities": [],
                    "affected_domains": [],
                    "affected_decisions": ["DEC-9999"],
                },
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        path = root / "decisions/DEC-9999-transition.md"
        path.write_text(decision_text("DEC-9999", "architecture"), encoding="utf-8")
        modified = {
            "filename": "decisions/DEC-9999-transition.md",
            "status": "modified",
            "base_content": decision_text("DEC-9999", "product"),
        }

        reporter = Reporter()
        validate_declared_scope(
            root,
            "- Change ID：CHG-9999",
            [modified],
            reporter,
        )

        scope_errors = [item for item in reporter.errors if item.code == "PR-SCOPE-002"]
        self.assertEqual(1, len(scope_errors), reporter.render("test"))
        self.assertIn("product", scope_errors[0].message)
        self.assertNotIn("PR-DECISION-001", reporter.render("test"))


if __name__ == "__main__":
    unittest.main()
