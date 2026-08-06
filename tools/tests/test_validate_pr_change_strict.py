from __future__ import annotations

import sys
import unittest

import yaml

from validation_test_utils import ROOT, copy_repo

sys.path.insert(0, str(ROOT / "tools"))
from diagnostics import Reporter  # noqa: E402
from validate_pr_change_strict import (  # noqa: E402
    required_change_types,
    validate_declared_scope,
)


class StrictPullRequestScopeTests(unittest.TestCase):
    def write_product_decision(self, root) -> str:
        path = "decisions/DEC-9999-product-test.md"
        file_path = root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            "---\n"
            "id: DEC-9999\n"
            "type: product\n"
            "status: accepted\n"
            "---\n\n"
            "# Product Decision\n",
            encoding="utf-8",
        )
        return path

    def declare_decision(self, root, change_id: str) -> None:
        path = next((root / "changes").glob(f"{change_id}-*/change.yaml"))
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["affected_decisions"] = ["DEC-9999"]
        path.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def test_product_change_can_modify_declared_product_decision(self) -> None:
        root = copy_repo(self)
        path = self.write_product_decision(root)
        self.declare_decision(root, "CHG-0004")
        reporter = Reporter()
        validate_declared_scope(root, "- Change ID：CHG-0004", [path], reporter)
        self.assertFalse(reporter.errors, reporter.render("test"))
        self.assertEqual({"product"}, required_change_types(root, path, Reporter()))

    def test_product_change_cannot_modify_undeclared_product_decision(self) -> None:
        root = copy_repo(self)
        path = self.write_product_decision(root)
        reporter = Reporter()
        validate_declared_scope(root, "- Change ID：CHG-0004", [path], reporter)
        self.assertTrue(any(item.code == "PR-DECISION-SCOPE-001" for item in reporter.errors))

    def test_governance_change_cannot_modify_product_decision(self) -> None:
        root = copy_repo(self)
        path = self.write_product_decision(root)
        reporter = Reporter()
        validate_declared_scope(root, "- Change ID：CHG-0006", [path], reporter)
        self.assertTrue(any(item.code == "PR-SCOPE-002" for item in reporter.errors))

    def test_governance_change_cannot_modify_security_policy(self) -> None:
        reporter = Reporter()
        validate_declared_scope(ROOT, "- Change ID：CHG-0006", ["SECURITY.md"], reporter)
        self.assertTrue(any(item.code == "PR-SCOPE-002" for item in reporter.errors))
        self.assertEqual({"security"}, required_change_types(ROOT, "SECURITY.md", Reporter()))


if __name__ == "__main__":
    unittest.main()
