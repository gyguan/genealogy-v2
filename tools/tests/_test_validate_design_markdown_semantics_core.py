from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0006-requirement-design-contract"


class DesignMarkdownSemanticsTests(unittest.TestCase):
    def test_nested_list_id_remains_visible(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("| SEC-GOV-DESIGN-001 |", "| SAFETY-GOV-DESIGN-001 |", 1)
        text = text.replace("| SEC-GOV-DESIGN-002 |", "| SAFETY-GOV-DESIGN-002 |", 1)
        text = text.replace(
            "## 安全与隐私",
            "## 安全与隐私\n\n- 安全控制\n    - SEC-GOV-DESIGN-NESTED：嵌套列表中的正式安全设计，关联 TEST-DESIGN-SEC-001。",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_security_cross_reference_does_not_require_repeated_test(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "## 迁移方案",
            "## 迁移方案\n\n迁移过程复用 SEC-GOV-DESIGN-001，不在此处重复定义安全测试。",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
