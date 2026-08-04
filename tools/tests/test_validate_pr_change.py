from __future__ import annotations

import sys
import unittest

from validation_test_utils import ROOT

sys.path.insert(0, str(ROOT / "tools"))
from diagnostics import Reporter  # noqa: E402
from validate_pr_change import extract_change_ids, required_change_types, validate_declared_scope  # noqa: E402


class PullRequestChangeValidationTests(unittest.TestCase):
    def test_extracts_only_explicit_change_declarations(self) -> None:
        body = "- Change ID：CHG-0006, CHG-0007\nContext mentions CHG-0004 but does not declare it"
        self.assertEqual({"CHG-0006", "CHG-0007"}, extract_change_ids(body))

    def test_historical_change_mention_does_not_expand_scope(self) -> None:
        reporter = Reporter()
        validate_declared_scope(
            ROOT,
            "- Change ID：CHG-0006\nHistorical context: CHG-0004",
            ["changes/CHG-0004-v01-recovery-loop/change.yaml"],
            reporter,
        )
        self.assertTrue(any(item.code == "PR-SCOPE-001" for item in reporter.errors))

    def test_governance_change_covers_tools_and_workflows(self) -> None:
        reporter = Reporter()
        validate_declared_scope(
            ROOT,
            "- Change ID：CHG-0006",
            ["tools/diagnostics.py", ".github/workflows/validate.yml"],
            reporter,
        )
        self.assertFalse(reporter.errors, reporter.render("test"))

    def test_governance_change_cannot_cover_product_assets(self) -> None:
        reporter = Reporter()
        validate_declared_scope(
            ROOT,
            "- Change ID：CHG-0006",
            ["product/releases.yaml"],
            reporter,
        )
        self.assertTrue(reporter.errors)
        self.assertEqual("PR-SCOPE-002", reporter.errors[0].code)

    def test_changed_change_asset_must_be_declared(self) -> None:
        reporter = Reporter()
        validate_declared_scope(
            ROOT,
            "- Change ID：CHG-0006",
            ["changes/CHG-0004-v01-recovery-loop/change.yaml"],
            reporter,
        )
        self.assertTrue(any(item.code == "PR-SCOPE-001" for item in reporter.errors))

    def test_path_classification_is_explicit(self) -> None:
        self.assertEqual({"product"}, required_change_types("product/releases.yaml"))
        self.assertEqual({"domain"}, required_change_types("domains/person-registry.md"))
        self.assertEqual({"governance", "engineering"}, required_change_types("tools/check.py"))


if __name__ == "__main__":
    unittest.main()
