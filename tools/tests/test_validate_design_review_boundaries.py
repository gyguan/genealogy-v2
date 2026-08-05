from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class DesignReviewBoundaryTests(unittest.TestCase):
    def test_blockquoted_code_does_not_supply_required_id(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("SEC-GOV-DESIGN-001", "SAFETY-GOV-DESIGN-001")
        text = text.replace("SEC-GOV-DESIGN-002", "SAFETY-GOV-DESIGN-002")
        text = text.replace(
            "## 安全与隐私",
            "## 安全与隐私\n\n>     SEC-GOV-DESIGN-EXAMPLE：引用块中的代码示例。",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("required facet security_privacy needs stable ID", result.stdout)

    def test_rule_cross_reference_is_not_definition(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "| TEST-DESIGN-001 | 正向 | 当前仓库和 CHG-0007 通过 | validate_design.py | SPEC-GOV-DESIGN-001 |",
            "| TEST-DESIGN-001 | 正向 | 当前仓库和 CHG-0007 通过 | validate_design.py | RULE-GOV-DESIGN-REFERENCE |",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
