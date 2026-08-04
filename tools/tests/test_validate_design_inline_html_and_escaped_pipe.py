from __future__ import annotations

import unittest

from validation_test_utils import copy_repo, run

CHANGE = "changes/CHG-0007-requirement-design-contract"


class InlineHtmlQuoteAndEscapedPipeTests(unittest.TestCase):
    def test_inline_html_remains_inside_lazy_quote_paragraph(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("MIG-GOV-DESIGN-001", "MIGRATION-GOV-DESIGN-001", 1)
        text = text.replace(
            "## 迁移方案\n\n",
            """## 迁移方案

> quoted migration example
<em>still quoted</em>
MIG-GOV-INLINE-HTML-001：该行仍属于引用段落。

""",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("required facet migration needs stable ID", result.stdout)

    def test_escaped_pipe_inside_table_cell_is_not_a_delimiter(self) -> None:
        root = copy_repo(self)
        path = root / CHANGE / "design.md"
        text = path.read_text(encoding="utf-8").replace(
            "AI 通过自由格式绕过约束",
            r"AI 通过自由格式 a \| b 绕过约束",
            1,
        )
        path.write_text(text, encoding="utf-8")

        result = run(root, "tools/validate_design.py")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
