from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class LazyQuoteAndSetextTests(unittest.TestCase):
    def test_lazy_blockquote_continuation_does_not_supply_id(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("MIG-GOV-DESIGN-001", "MIGRATION-GOV-DESIGN-001", 1)
        text = text.replace(
            "## 迁移方案\n\n",
            """## 迁移方案

> quoted migration example
MIG-GOV-LAZY-001：该行是引用段落的 lazy continuation。

""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("required facet migration needs stable ID", result.stdout)

    def test_setext_heading_closes_paragraph_before_type7_html(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("MIG-GOV-DESIGN-001", "MIGRATION-GOV-DESIGN-001", 1)
        text = text.replace(
            "## 迁移方案\n\n",
            """## 迁移方案

迁移标题
========
<widget>
MIG-GOV-SETEXT-001：该内容位于原始 HTML 块。

""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("required facet migration needs stable ID", result.stdout)


if __name__ == "__main__":
    unittest.main()
